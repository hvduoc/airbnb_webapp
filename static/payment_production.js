// JavaScript cho Payment Ledger Production Version

let currentUser = null;
let recipients = [];
let teamMembers = [];

// Khởi tạo ứng dụng
document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
});

async function initializeApp() {
    try {
        await loadUserInfo();
        showTab('dashboard');
        updateClock();
        setInterval(updateClock, 1000);
    } catch (error) {
        console.error('Initialization error:', error);
        window.location.href = '/login';
    }
}

async function loadUserInfo() {
    try {
        // Test auth trước
        const authResponse = await axios.get('/api/test-auth');
        console.log('Auth test:', authResponse.data);

        if (authResponse.data.status !== 'authenticated') {
            throw new Error('Not authenticated');
        }

        // Load dashboard sẽ fail nếu không authenticate
        await loadDashboard();
        await loadRecipients();
        await loadTeamMembers();
    } catch (error) {
        console.error('Load user info error:', error);
        throw error;
    }
}

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleString('vi-VN');
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

// Quản lý tab
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });

    document.getElementById(`${tabName}-tab`).classList.remove('hidden');

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('border-green-500', 'text-green-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });

    document.querySelector(`[data-tab="${tabName}"]`).classList.remove('border-transparent', 'text-gray-500');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('border-green-500', 'text-green-600');

    if (tabName === 'payments-list') {
        loadPayments();
    } else if (tabName === 'handover-list') {
        loadHandovers();
    } else if (tabName === 'team') {
        loadTeamMembers();
    }
}

// Load dashboard
async function loadDashboard() {
    try {
        const response = await axios.get('/api/dashboard');
        const data = response.data;

        // Update user info from response if available
        if (!currentUser) {
            // Get user info from another endpoint or set default
            currentUser = { name: "User", role: "unknown" };
        }

        document.getElementById('totalCollected').textContent = formatCurrency(data.total_collected);
        document.getElementById('collectionRate').textContent = `${data.collection_rate}%`;
        document.getElementById('cashPending').textContent = formatCurrency(data.cash_pending_handover);
        document.getElementById('totalHandovers').textContent = data.total_handovers;

    } catch (error) {
        console.error('Không thể tải dashboard:', error);
        if (error.response?.status === 401) {
            window.location.href = '/login';
        }
    }
}

// Load danh sách người nhận
async function loadRecipients() {
    try {
        const response = await axios.get('/api/recipients');
        recipients = response.data.recipients;

        const select = document.getElementById('recipientId');
        if (select) {
            select.innerHTML = '<option value="">Chọn người nhận</option>';

            recipients.forEach(recipient => {
                const option = document.createElement('option');
                option.value = recipient.id;
                option.textContent = `${recipient.name} - ${recipient.role} (${recipient.phone})`;
                select.appendChild(option);
            });
        }

    } catch (error) {
        console.error('Không thể tải danh sách người nhận:', error);
    }
}

// Load danh sách team
async function loadTeamMembers() {
    try {
        const response = await axios.get('/api/users');
        teamMembers = response.data.users;

        displayTeamMembers();

    } catch (error) {
        console.error('Không thể tải danh sách team:', error);
        // Nếu không có quyền xem team, ẩn tab
        const teamTab = document.getElementById('teamTab');
        if (teamTab && error.response?.status === 403) {
            teamTab.style.display = 'none';
        }
    }
}

function displayTeamMembers() {
    const container = document.getElementById('teamListContainer');
    if (!container) return;

    container.innerHTML = '';

    if (teamMembers.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-8">Không có quyền xem danh sách team</p>';
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4';

    teamMembers.forEach(member => {
        const card = document.createElement('div');
        card.className = 'bg-white border rounded-lg p-4 hover:shadow-md transition-shadow';

        const roleClass = `role-${member.role}`;

        card.innerHTML = `
            <div class="flex items-center space-x-3">
                <div class="flex-shrink-0">
                    <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <i class="fas fa-user text-gray-600"></i>
                    </div>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                        ${member.full_name}
                    </p>
                    <p class="text-sm text-gray-500 truncate">
                        @${member.username}
                    </p>
                </div>
                <div class="flex-shrink-0">
                    <span class="role-badge ${roleClass}">
                        ${member.role_display}
                    </span>
                </div>
            </div>
            
            <div class="mt-3 text-sm text-gray-600">
                ${member.phone ? `<p><i class="fas fa-phone mr-2"></i>${member.phone}</p>` : ''}
                ${member.email ? `<p><i class="fas fa-envelope mr-2"></i>${member.email}</p>` : ''}
            </div>
        `;

        grid.appendChild(card);
    });

    container.appendChild(grid);
}

// Xử lý form ghi nhận thu
document.getElementById('paymentForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append('booking_id', document.getElementById('bookingId').value);
    formData.append('guest_name', document.getElementById('guestName').value);
    formData.append('amount_due', document.getElementById('amountDue').value);
    formData.append('amount_collected', document.getElementById('amountCollected').value);
    formData.append('payment_method', document.getElementById('paymentMethod').value);
    formData.append('collected_by', document.getElementById('collectedBy').value);
    formData.append('notes', document.getElementById('notes').value);

    const receiptImage = document.getElementById('receiptImage')?.files[0];
    if (receiptImage) {
        formData.append('receipt_image', receiptImage);
    }

    try {
        const response = await axios.post('/api/payments', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        if (response.data.success) {
            showToast('Đã lưu khoản thu thành công!', 'success');
            resetPaymentForm();
            await loadDashboard();
        }

    } catch (error) {
        console.error('Payment submission error:', error);
        if (error.response?.status === 401) {
            showToast('Phiên đăng nhập đã hết hạn', 'error');
            setTimeout(() => window.location.href = '/login', 2000);
        } else {
            showToast('Không thể lưu khoản thu', 'error');
        }
    }
});

// Xử lý form bàn giao
document.getElementById('handoverForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append('recipient_user_id', document.getElementById('recipientId').value);
    formData.append('amount', document.getElementById('handoverAmount').value);
    formData.append('notes', document.getElementById('handoverNotes').value);

    const handoverImage = document.getElementById('handoverImage')?.files[0];
    if (handoverImage) {
        formData.append('handover_image', handoverImage);
    }

    try {
        const response = await axios.post('/api/handovers', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        if (response.data.success) {
            showToast('Đã bàn giao thành công!', 'success');
            resetHandoverForm();
            await loadDashboard();
        }

    } catch (error) {
        console.error('Handover submission error:', error);
        if (error.response?.status === 401) {
            showToast('Phiên đăng nhập đã hết hạn', 'error');
            setTimeout(() => window.location.href = '/login', 2000);
        } else {
            showToast('Không thể thực hiện bàn giao', 'error');
        }
    }
});

function resetPaymentForm() {
    document.getElementById('paymentForm')?.reset();
}

function resetHandoverForm() {
    document.getElementById('handoverForm')?.reset();
}

async function loadPayments() {
    try {
        const response = await axios.get('/api/payments');
        const payments = response.data.payments;

        const tbody = document.getElementById('paymentsTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        payments.forEach(payment => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${formatDateTime(payment.timestamp)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${payment.booking_id}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${payment.guest_name}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${formatCurrency(payment.amount_due)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${formatCurrency(payment.amount_collected)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${getPaymentMethodText(payment.payment_method)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${payment.collected_by}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${payment.receipt_image ?
                    `<button onclick="showImage('${payment.receipt_image}')" class="text-green-600 hover:text-green-800">
                            <i class="fas fa-image"></i> Xem ảnh
                        </button>` :
                    '<span class="text-gray-400">Không có</span>'
                }
                </td>
            `;
            tbody.appendChild(row);
        });

    } catch (error) {
        console.error('Không thể tải danh sách thu:', error);
        if (error.response?.status === 401) {
            window.location.href = '/login';
        }
    }
}

async function loadHandovers() {
    try {
        const response = await axios.get('/api/handovers');
        const handovers = response.data.handovers;

        const container = document.getElementById('handoverListContainer');
        if (!container) return;

        container.innerHTML = '';

        if (handovers.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">Chưa có bàn giao nào</p>';
            return;
        }

        handovers.forEach(handover => {
            const card = document.createElement('div');
            card.className = 'handover-card bg-white border rounded-lg p-4 mb-4';
            card.innerHTML = `
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <h3 class="font-semibold text-lg">Bàn giao #${handover.id}</h3>
                        <p class="text-gray-600">${formatDateTime(handover.timestamp)}</p>
                    </div>
                    <span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm">
                        ${handover.status === 'completed' ? 'Hoàn thành' : 'Đang xử lý'}
                    </span>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                    <div>
                        <p class="text-sm text-gray-600">Người bàn giao:</p>
                        <p class="font-medium">${handover.handover_by}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-600">Người nhận:</p>
                        <p class="font-medium">${handover.recipient_name}</p>
                        <p class="text-sm text-gray-500">${handover.recipient_phone}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-600">Số tiền:</p>
                        <p class="font-bold text-lg text-green-600">${formatCurrency(handover.amount)}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-600">Trạng thái ký nhận:</p>
                        <p class="font-medium ${handover.signature_status === 'signed' ? 'text-green-600' : 'text-yellow-600'}">
                            ${handover.signature_status === 'signed' ? 'Đã ký nhận' : 'Chờ ký nhận'}
                        </p>
                    </div>
                </div>
                
                ${handover.notes ? `
                    <div class="mb-3">
                        <p class="text-sm text-gray-600">Ghi chú:</p>
                        <p class="text-sm">${handover.notes}</p>
                    </div>
                ` : ''}
                
                ${handover.handover_image ? `
                    <div class="mb-3">
                        <button onclick="showImage('${handover.handover_image}')" 
                                class="text-green-600 hover:text-green-800 text-sm">
                            <i class="fas fa-image mr-1"></i> Xem hình ảnh bàn giao
                        </button>
                    </div>
                ` : ''}
            `;
            container.appendChild(card);
        });

    } catch (error) {
        console.error('Không thể tải danh sách bàn giao:', error);
        if (error.response?.status === 401) {
            window.location.href = '/login';
        }
    }
}

async function logout() {
    try {
        await axios.post('/api/logout');
        window.location.href = '/login';
    } catch (error) {
        console.error('Lỗi đăng xuất:', error);
        // Force redirect anyway
        window.location.href = '/login';
    }
}

// Hiển thị hình ảnh
function showImage(imagePath) {
    document.getElementById('modalImage').src = imagePath;
    document.getElementById('imageModal').classList.remove('hidden');
}

function closeImageModal() {
    document.getElementById('imageModal').classList.add('hidden');
}

// Các hàm tiện ích
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN');
}

function getPaymentMethodText(method) {
    const methods = {
        'cash': 'Tiền mặt',
        'bank_transfer': 'Chuyển khoản',
        'airbnb_payout': 'Airbnb',
        'momo': 'MoMo',
        'zalopay': 'ZaloPay',
        'vnpay': 'VNPay'
    };
    return methods[method] || method;
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const icon = document.getElementById('toastIcon');
    const messageEl = document.getElementById('toastMessage');

    if (!toast || !icon || !messageEl) return;

    messageEl.textContent = message;

    if (type === 'success') {
        icon.className = 'fas fa-check-circle text-green-500 text-xl';
    } else if (type === 'error') {
        icon.className = 'fas fa-exclamation-circle text-red-500 text-xl';
    } else {
        icon.className = 'fas fa-info-circle text-blue-500 text-xl';
    }

    toast.classList.remove('hidden');

    setTimeout(() => {
        hideToast();
    }, 5000);
}

function hideToast() {
    const toast = document.getElementById('toast');
    if (toast) {
        toast.classList.add('hidden');
    }
}

// Đóng modal khi click bên ngoài
document.getElementById('imageModal')?.addEventListener('click', function (e) {
    if (e.target === this) {
        closeImageModal();
    }
});