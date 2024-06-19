
let errors = $('.alert').length > 0

if (errors){
   $('.drop').addClass('show marg-form-dropdown')
}

$('#dropLink').click(function (){
    $('.drop').removeClass('marg-form-dropdown')
})
