$('.delete-btn').click(function () {
    deleteForm = $(this).closest('form');
    $('#deleteConfirmModal').modal('show');
});

$('#confirmDelete').click(function () {
    deleteForm.submit();
});