$('#add-btn').click(function () {
    $('#attributes-div').append(
        '<div class="d-flex mx-5 mb-3">' +
        '   <div class="d-flex align-items-center">' +
        '       <label for="id_name" class="w-75">Название атрибута</label>' +
        '       <input type="text" class="form-control" id="id_name" name="name">' +
        '   </div>' +
        '   <div class="d-flex ms-5 align-items-center">' +
        '       <label for="id_value" class="w-75">Значение атрибута</label>' +
        '       <input type="text" class="form-control" id="id_value" name="value">' +
        '   </div>' +
        '</div>'
    )
});

$('#del-btn').click(function () {
    $('#attributes-div').children().last().remove();
})