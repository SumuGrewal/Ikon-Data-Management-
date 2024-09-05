
document.addEventListener('DOMContentLoaded', function() {
    const fileEntries = document.querySelectorAll('.file-entry');
    const checklistItems = document.getElementById('checklist-items');
    const progressFill = document.getElementById('progress-fill');
    const progressPercentage = document.getElementById('progress-percentage');

    fileEntries.forEach(entry => {
        entry.addEventListener('click', function() {
            const fileNumber = this.dataset.fileNumber;
            loadChecklist(fileNumber);
            loadProgress(fileNumber);
        });
    });

    function loadChecklist(fileNumber) {
        fetch(`/api/client_files/${fileNumber}/checklist`)
            .then(response => response.json())
            .then(data => {
                checklistItems.innerHTML = '';
                data.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item.description;
                    li.dataset.itemId = item.id;
                    li.classList.add(item.status);
                    li.addEventListener('click', function() {
                        toggleChecklistItem(item.id);
                    });
                    checklistItems.appendChild(li);
                });
            });
    }

    function toggleChecklistItem(itemId) {
        const li = document.querySelector(`li[data-item-id="${itemId}"]`);
        const newStatus = li.classList.contains('completed') ? 'pending' : 'completed';
        fetch(`/api/checklist_items/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus }),
        })
        .then(response => response.json())
        .then(data => {
            li.classList.toggle('completed');
            li.classList.toggle('pending');
            loadProgress(document.querySelector('.file-entry.active').dataset.fileNumber);
        });
    }

    function loadProgress(fileNumber) {
        fetch(`/api/client_files/${fileNumber}/progress`)
            .then(response => response.json())
            .then(data => {
                progressFill.style.width = `${data.progress}%`;
                progressPercentage.textContent = `${Math.round(data.progress)}%`;
            });
    }
});