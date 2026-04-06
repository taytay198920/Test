// 页面加载时获取下拉框选项和已有测试组
document.addEventListener("DOMContentLoaded", async function() {

    // 使用事件委托处理所有全选/取消全选按钮
    document.body.addEventListener('click', function(e) {
        // PowerManagement 全选
        if (e.target.classList && e.target.classList.contains('select-all-power')) {
            const modal = e.target.closest('.modal')
            if (modal) {
                modal.querySelectorAll('.power-checkbox').forEach(cb => cb.checked = true)
            }
        }

        // PowerManagement 取消全选
        if (e.target.classList && e.target.classList.contains('deselect-all-power')) {
            const modal = e.target.closest('.modal')
            if (modal) {
                modal.querySelectorAll('.power-checkbox').forEach(cb => cb.checked = false)
            }
        }

        // MTU1500 全选
        if (e.target.classList && e.target.classList.contains('mtu1500-select-all')) {
            const mtuSection = e.target.closest('.mtu-section')
            if (mtuSection) {
                mtuSection.querySelectorAll('.mtu1500-protocol-checkbox, .mtu1500-speed-checkbox').forEach(cb => cb.checked = true)
            }
        }

        // MTU1500 取消全选
        if (e.target.classList && e.target.classList.contains('mtu1500-deselect-all')) {
            const mtuSection = e.target.closest('.mtu-section')
            if (mtuSection) {
                mtuSection.querySelectorAll('.mtu1500-protocol-checkbox, .mtu1500-speed-checkbox').forEach(cb => cb.checked = false)
            }
        }

        // MTU9000 全选
        if (e.target.classList && e.target.classList.contains('mtu9000-select-all')) {
            const mtuSection = e.target.closest('.mtu-section')
            if (mtuSection) {
                mtuSection.querySelectorAll('.mtu9000-protocol-checkbox, .mtu9000-speed-checkbox').forEach(cb => cb.checked = true)
            }
        }

        // MTU9000 取消全选
        if (e.target.classList && e.target.classList.contains('mtu9000-deselect-all')) {
            const mtuSection = e.target.closest('.mtu-section')
            if (mtuSection) {
                mtuSection.querySelectorAll('.mtu9000-protocol-checkbox, .mtu9000-speed-checkbox').forEach(cb => cb.checked = false)
            }
        }

        // Save config button - 验证并保存配置
        if (e.target.classList && e.target.classList.contains('save-config-btn')) {
            const groupId = e.target.getAttribute('data-group-id')
            const modal = document.querySelector(`#config_${groupId}`)

            // 先验证配置
            if (validateIperfConfig(modal)) {
                // 验证通过，保存配置（这里可以调用保存API，或只是关闭模态框）
                console.log(`配置验证通过，保存 group ${groupId} 的配置`)

                // 关闭模态框
                const bootstrapModal = bootstrap.Modal.getInstance(modal)
                if (bootstrapModal) {
                    bootstrapModal.hide()
                } else {
                    // 如果获取不到实例，使用jQuery方式或直接移除backdrop
                    modal.querySelector('.btn-close').click()
                }
            }
        }

        if (e.target.classList && e.target.classList.contains('run-test-btn')) {
            const groupId = e.target.getAttribute('data-group-id')
            console.log("groupId", groupId)
            runTest(e, groupId)
        }
    })
})

// 验证 iperf 配置：每个 MTU 的 protocols 和 speeds 必须同时为空或同时非空
function validateIperfConfig(modal) {
    // 验证 MTU1500
    const mtu1500Protocols = modal.querySelectorAll('.mtu1500-protocol-checkbox:checked')
    const mtu1500Speeds = modal.querySelectorAll('.mtu1500-speed-checkbox:checked')
    const mtu1500Valid = (mtu1500Protocols.length === 0 && mtu1500Speeds.length === 0) ||
                         (mtu1500Protocols.length > 0 && mtu1500Speeds.length > 0)

    // 验证 MTU9000
    const mtu9000Protocols = modal.querySelectorAll('.mtu9000-protocol-checkbox:checked')
    const mtu9000Speeds = modal.querySelectorAll('.mtu9000-speed-checkbox:checked')
    const mtu9000Valid = (mtu9000Protocols.length === 0 && mtu9000Speeds.length === 0) ||
                         (mtu9000Protocols.length > 0 && mtu9000Speeds.length > 0)

    // 收集错误信息
    const errors = []
    if (!mtu1500Valid) {
        errors.push('MTU=1500：协议和速率必须同时选择或同时不选')
    }
    if (!mtu9000Valid) {
        errors.push('MTU=9000：协议和速率必须同时选择或同时不选')
    }

    if (errors.length > 0) {
        alert('配置验证失败：\n' + errors.join('\n'))
        return false
    }

    return true
}

// 收集配置数据并发送到后端
async function runTest(e, groupId) {
    // 找到对应的模态框
    const modal = document.querySelector(`#config_${groupId}`)
    if (!modal) {
        console.error('Modal not found for group:', groupId)
        return
    }

    // 收集配置数据
    const configData = {
        group_id: groupId,
        // basic_test: {
        //     ping_test: modal.querySelector(`#pingTest_${groupId}`)?.checked || false
        // },
        // power_management: {
        //     restart: modal.querySelector(`#restartTest_${groupId}`)?.checked || false,
        //     shutdown: modal.querySelector(`#shutdownTest_${groupId}`)?.checked || false,
        //     sleep: modal.querySelector(`#sleepTest_${groupId}`)?.checked || false
        // },
        // iperf_test: {
        //     mtu1500: {
        //         protocols: [],
        //         speeds: []
        //     },
        //     mtu9000: {
        //         protocols: [],
        //         speeds: []
        //     }
        // }
        basic_test: [],
        power_management: [],
        mtu1500: {
            protocols: [],
            speeds: []
        },
        mtu9000: {
            protocols: [],
            speeds: []
        }

    }
    const ping_test = modal.querySelector(`#pingTest_${groupId}:checked`)
    if (ping_test) configData.basic_test.push("ping_test")

    const restart = modal.querySelector(`#restartTest_${groupId}:checked`)
    if (restart) configData.power_management.push("restart_test")

    const shutdown = modal.querySelector(`#shutdownTest_${groupId}:checked`)
    if (shutdown) configData.power_management.push("shutdown_test")

    const sleep = modal.querySelector(`#sleepTest_${groupId}:checked`)
    if (sleep) configData.power_management.push("sleep_test")

    // 收集 MTU1500 的协议
    const mtu1500Protocols = modal.querySelectorAll('.mtu1500-protocol-checkbox:checked')
    mtu1500Protocols.forEach(cb => {
        configData.mtu1500.protocols.push(cb.value)
    })

    // 收集 MTU1500 的速率
    const mtu1500Speeds = modal.querySelectorAll('.mtu1500-speed-checkbox:checked')
    mtu1500Speeds.forEach(cb => {
        configData.mtu1500.speeds.push(cb.value)
    })

    // 收集 MTU9000 的协议
    const mtu9000Protocols = modal.querySelectorAll('.mtu9000-protocol-checkbox:checked')
    mtu9000Protocols.forEach(cb => {
        configData.mtu9000.protocols.push(cb.value)
    })

    // 收集 MTU9000 的速率
    const mtu9000Speeds = modal.querySelectorAll('.mtu9000-speed-checkbox:checked')
    mtu9000Speeds.forEach(cb => {
        configData.mtu9000.speeds.push(cb.value)
    })

    // 同时收集当前选中的硬件配置（Client、Server、Switch、Cable）
    const row = e.target.closest('tr')
    if (row) {
        configData.hardware = {
            client_id: row.querySelector('select:first-child')?.value,
            server_id: row.querySelectorAll('select')[1]?.value,
            switch_id: row.querySelectorAll('select')[2]?.value,
            cable_id: row.querySelectorAll('select')[3]?.value,
            test_bundle: row.querySelector('input[type="text"]')?.value
        }
    }

    console.log('Sending config data:', configData)

    try {
        // 发送到后端
        const response = await fetch('/api/test/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        })

        const result = await response.json()

        if (result.success) {
            // 更新状态显示
            updateGroupStatus(groupId, 'running')

        } else {
            console.error("Test start failed!")
        }
    } catch (error) {
        console.error('Error running test:', error)
    }
}

// 更新组状态
function updateGroupStatus(groupId, status) {
    const row = document.querySelector(`button[data-group-id="${groupId}"]`).closest('tr')
    if (row) {
        const statusSpan = row.querySelector('.badge')
        if (statusSpan) {
            statusSpan.textContent = status
            // 更新样式类
            statusSpan.className = 'badge rounded-pill '
            if (status === 'ready') {
                statusSpan.classList.add('text-bg-warning')
            } else if (status === 'running') {
                statusSpan.classList.add('bg-primary')
            } else if (status === 'completed') {
                statusSpan.classList.add('bg-success')
            }
        }
    }
}
