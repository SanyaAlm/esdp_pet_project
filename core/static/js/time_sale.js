let startDateInp = $('#start_date')
let endDateInp = $('#end_date')
let token = localStorage.getItem('Token')

let now = new Date()
let currentDate = now.toISOString().slice(0,16)
let productId = $('#product').val()
startDateInp.attr('min', currentDate)
endDateInp.attr('min', currentDate)
let addBtn = $('#add-discount')

checkSale(productId)

addBtn.click(function (){
    $('#discountModal').show()
})



$('#make_sale').click(function () {
        let startDate = startDateInp.val()
        let endDate = endDateInp.val()
        let product = $('#product').val()
        let discountPercent = $('#percent').val()
        let discountCurrency = $('#currency').val()

        $.ajax({
            url: `https://market.shopuchet.kz/api/time_discount/`,
            method: "POST",
            data: {
                product: product,
                start_date: startDate,
                end_date: endDate,
                discount: discountPercent,
                discount_in_currency: discountCurrency
            },
            headers: {
                'Authentication': `Token ${token}`
            }

        }).then(function (){
            $('#discountModal').hide()
            let discountBtn =  $('#add-discount')
            discountBtn.hide()
            $('#delete-btn').show()
            checkTimeDiscountField(product)
        }).catch(function (error){
            console.log(error)
            if (error.responseJSON){
                let errorMessages = []
                if (error.responseJSON.start_date){
                    errorMessages.push(error.responseJSON.start_date[0])
                }
                if (error.responseJSON.end_date){
                    errorMessages.push(error.responseJSON.end_date[0])
                }
                if (error.responseJSON.discount){
                    errorMessages.push(error.responseJSON.discount[0])
                }
                if (error.responseJSON.non_field_errors) {
                    errorMessages.push(error.responseJSON.non_field_errors[0])
                }
                if (error.responseJSON.discount_in_currency) {
                    errorMessages.push(error.responseJSON.discount_in_currency[0])
                }
                if (errorMessages.length > 0) {
                    let errorDiv = $('#error-messages')
                    errorDiv.html(errorMessages.join('<br>'))
                    errorDiv.show()
                }
            }
            else {
                console.log(error)
            }

        })

})

$('#delete-btn').click(function (){
    let productId = $('#product').val()
    getSaleId(productId).then(function (data) {
            let discountId = data.discount_id
            if (discountId) {
                $('#delete_modal').show()
            } else {
                alert('Скидка уже удалена')
            }
        })
})

function getSaleId (productId) {
     return $.ajax({
            url: `https://market.shopuchet.kz/api/time_discount/get-discount-by-product/?product_id=${productId}`,
            method: 'GET',
            headers: {
                'Authentication': `Token ${token}`
            }
        })
}

$('#delete_sale').click(function (){
    let productId = $('#product').val()

        getSaleId(productId).then(function (data) {
            let discountId = data.discount_id
            if (discountId) {
                $.ajax({
                    url: `https://market.shopuchet.kz/api/time_discount/${discountId}/`,
                    method: "DELETE",
                    headers: {
                        'Authentication': `Token ${token}`
                    }
                }).then(function () {
                    $('#delete_modal').hide()
                    $('#delete-btn').hide()
                    $('#add-discount').show()
                    checkConstantSale(productId)
                })
            } else {
                alert('Скидка уже удалена')
            }
        })
})

function checkConstantSale(productId){
     $.ajax({
        url: `https://market.shopuchet.kz/api/product/${productId}/`,
        method: 'GET',
        headers: {
            'Authentication': `Token ${token}`
        }
    }).then(function (data){
        if (data.discount && data.discount > 0) {
                $('#productPrice').html( `<del class="text-secondary fs-4">${data.price} ₸</del> <p class="fs-3 m-0" style="font-weight: 500">${data.discounted_price} ₸</p><p class="text-success fs-5">Скидка: ${data.discount}%</p>`)
        }
        else {
            $('#productPrice').html(`<div id="priceDiscount">\n` +
                `                            <p id="price" class="fs-3">${data.price} ₸</p>\n` +
                `                        </div>`)
        }

     })
}


function checkTimeDiscountField(productId) {
    getSaleId(productId).then(function (data) {
        let discountId = data.discount_id;
        let productPrice = $('#somePrice').val();
        if (discountId) {
            $.ajax({
                url: `https://market.shopuchet.kz/api/time_discount/${discountId}/`,
                method: "GET",
                headers: {
                    'Authentication': `Token ${token}`
                }
            }).then(function (data) {
                checkStartDiscount(productId).then(function (started) {
                    if (started) {
                        if (data.discount) {
                            $('#productPrice').html(`<del class="text-secondary fs-4">${productPrice} ₸</del> <p class="fs-3 m-0" style="font-weight: 500">${data.discounted_price} ₸</p><p class=" text-success fs-5">Скидка: ${data.discount}%</p>`);
                        } else if (data.discount_in_currency) {
                            $('#productPrice').html(` <del class="text-secondary fs-4">${productPrice} ₸</del> <p class="fs-3 m-0" style="font-weight: 500">${data.discounted_price} ₸</p><p class=" text-success fs-5">Скидка: ${data.discount_in_currency} ₸</p>`);
                        }
                    }
                });
            });
        }
    });
}

function checkStartDiscount(productId){
    return getSaleId(productId).then(function (data){
        let discountId = data.discount_id
        if (discountId){
            return $.ajax({
                url: `https://market.shopuchet.kz/api/time_discount/${discountId}/check-start`,
                method: "GET",
                headers: {
                    'Authentication': `Token ${token}`
                }
            }).then(function (data){
                return !!data.started;

            })
        }
        return false
    })
}

$('.close-btn').click(function (){
     $('#discountModal').hide()
    $('#delete_modal').hide()
})

function checkSale(productId){
    getSaleId(productId).then(function (data) {
        if (data.error){
            $('#delete-btn').hide()
        $('#add-discount').show()
        checkConstantSale(productId)

        }
        else {
            $('#delete-btn').show()
            $('#add-discount').hide()
            checkTimeDiscountField(productId)

        }
    })
}

setInterval(function (){
    let productId = $('#product').val()
    checkSale(productId)
}, 3000)


