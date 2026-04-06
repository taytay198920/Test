document.addEventListener('DOMContentLoaded', function () {
    // 事件委托：监听整个表格上的点击事件
    document.querySelector('.table').addEventListener('click', function (e) {
        const deleteBtn = e.target.closest('[data-switch-id]')
        if (!deleteBtn) return

        const switchId = deleteBtn.dataset.switchId
        e.preventDefault()

        if (confirm(`Are you sure you want to delete this switch?`)) {
            fetch(`/api/switches/delete/${switchId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
                .then(response => {
                    if (response.redirected) {
                        window.location.href = response.url
                    }
                })
                .catch(error => {
                    console.error('Error:', error)
                    alert('Delete failed!')
                })
        }
    })
})