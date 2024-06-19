function phoneStandard() {
    let phoneInput = $('input[name="phone"]');

    phoneInput.on('input', function () {
      let inputValue = $(this).val();

      if (!inputValue.startsWith('+77')) {
        inputValue = '+77' + inputValue;
        $(this).val(inputValue);
      }
    });
  }
phoneStandard()


