function order() {
    let products = $('#cart-products').val()
    let shop = $('#shop').val()
    let total = $('#form-total').val()
    let payer_name = $('#id_payer_name').val()
    let payer_surname = $('#id_payer_surname').val()
    let payer_phone = $('#id_payer_phone').val()
    let payer_email = $('#id_payer_email').val()
    let payer_address = $('#id_payer_address').val()
    let payer_city = $('#id_payer_city').val()
    let payer_postal_code = $('#id_payer_postal_code').val()
    let account = $('#user-id').val()
    $.ajax({
        url: 'https://market.shopuchet.kz/api/order/create_order/',
        method: 'POST',
        data: {
            products,
            shop,
            total,
            payer_name,
            payer_surname,
            payer_phone,
            payer_email,
            payer_address,
            payer_city,
            payer_postal_code,
            account
        },
    }).then(function(data) {
        pay(data['order_id'], parseFloat(total), payer_phone, data['user_id'], payer_email)
    }).catch(
        function(error) {
            console.log(error)
        }
    )
}

let pay = function(orderId, total, payer_phone, account, payer_email) {
    var widget = new cp.CloudPayments();
    widget.pay('charge', {
        publicId: 'pk_3d2e6006deeae8feba63160d9efd2',
        description: 'Оплата товаров в example.com',
        amount: total,
        currency: 'KZT',
        accountId: account,
        invoiceId: orderId,
        skin: "classic",
        payer: {
            phone: payer_phone,
        }
    }).then(function(widgetResult) {
        if (widgetResult && widgetResult.success) {
            console.log('Payment successful', widgetResult);

            $.ajax({
                url: 'https://market.shopuchet.kz/api/create-check/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ order_id: orderId, email: payer_email }),
                success: function(response) {
                    console.log('Server response', response);
                },
                error: function(error) {
                    console.error('Error in AJAX request', error);
                }
            });

            window.location.reload();
        } else {
            console.log('Payment not successful or cancelled');
        }
    }).catch(function(error) {
        console.log('Payment error', error);
    });
};


$('#checkout').click(order);