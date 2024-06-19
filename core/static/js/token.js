$('#loginForm').submit(function (event) {
    let email = $('#id_username').val()
    let password = $('#id_password').val()
    let token
    $.ajax({
        url: 'https://market.shopuchet.kz/api/login/',
        method: 'POST',
        data: {
            username: email,
            password: password
        }
    }).then(function (data) {
        token = data.token
        localStorage.setItem('Token', token)
    }).catch(function (error) {
        console.log(error)
    })

})

$('#logout').click(function logOut(e) {
    $.ajax({
        url: 'https://market.shopuchet.kz/api/logout/',
        method: 'post',
        headers: {'Authorization': 'Token ' + localStorage.getItem('Token')},
        dataType: 'json',
    }).then(function () {
        localStorage.removeItem('Token')
    });
})
