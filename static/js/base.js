// 输入框验证错误显示
(() => {
    'use strict'

    const forms = document.querySelectorAll('.needs-validation')

    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if(!form.checkValidity()){
                event.preventDefault()
                event.stopPropagation()
            }

            form.classList.add('was-validated')
            }, false)
        })

    document.querySelectorAll('.tooltip-info')
        .forEach(tooltip => {
            new bootstrap.Tooltip(tooltip, {
                selector: '[data-bs-toggle="tooltip"]'
            })
        })
})()

// Alert自动关闭
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        const alert = document.getElementById('autoCloseAlert');
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 3000)
});
