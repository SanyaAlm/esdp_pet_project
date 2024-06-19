$(document).ready(function () {
    $('.otp-card-inputs input').keyup(function (e) {
        if ($(this).val().length == $(this).attr('maxlength') && $(this).next().length) {
            $(this).next('input').focus();
        }
    });
    let userId = $('#userId').val()
    let isRequestSent = localStorage.getItem('isRequestSent')
    if (isRequestSent !== userId){
    $.ajax({
        url: `https://market.shopuchet.kz/sms/send/${userId}`,
        method: 'POST',
        success: function (resp){
            console.log(`success ${resp}`)
            localStorage.setItem('isRequestSent', userId)
        },
        error: function (err) {
            console.log(`fail ${err}`)
        }
})}
})

let startTime = 60 * 1000;
let timerElement = $('#timer');
let sendButton = $('#sendButton');

function updateTimer(timeRemaining) {
    const minutes = Math.floor(timeRemaining / 60000);
    const seconds = Math.floor((timeRemaining % 60000) / 1000);

    timerElement.text(`${minutes}:${seconds < 10 ? '0' : ''}${seconds}`);
}

function showSendButton() {
    sendButton.show()
    sendButton.addClass('d-block');
}

function hideSendButton() {
    sendButton.hide()
    sendButton.removeClass('d-block');
}

function countdown() {
    updateTimer(startTime);

    const intervalId = setInterval(() => {
        startTime -= 1000;
        updateTimer(startTime);

        if (startTime <= 0) {
            clearInterval(intervalId);
            showSendButton();
        }
    }, 1000);
}

function resetTimer() {
    startTime = 60 * 1000;
    hideSendButton();
    countdown();
}

sendButton.on('click', function(event) {
    event.preventDefault()
    resetTimer();
     let userId = $('#userId').val()
    $.ajax({
        url: `https://market.shopuchet.kz/sms/send/${userId}`,
        method: 'POST',
        success: function (resp){
            console.log(`success ${resp}`)
            localStorage.setItem('isRequestSent', userId)
        },
        error: function (err) {
            console.log(`fail ${err}`)
        }})
});

countdown();
