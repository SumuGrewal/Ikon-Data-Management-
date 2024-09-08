document.addEventListener('DOMContentLoaded', function() {
    // Fetch client files and populate the file list
    fetch('/api/client_files')
        .then(response => response.json())
        .then(files => {
            const fileList = document.getElementById('file-list');
            files.forEach(file => {
                const li = document.createElement('li');
                li.textContent = file.file_number;
                li.addEventListener('click', () => loadChecklist(file.id));
                fileList.appendChild(li);
            });
        });

    function loadChecklist(fileId) {
        fetch(`/api/checklist/${fileId}`)
            .then(response => response.json())
            .then(checklistItems => {
                const checklist = document.getElementById('checklist-items');
                checklist.innerHTML = ''; // Clear existing items
                checklistItems.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item.description;
                    checklist.appendChild(li);
                });
                document.getElementById('selected-file').textContent = fileId;
                updateProgress(fileId);
            });
    }

    function updateProgress(fileId) {
        fetch(`/api/checklist/${fileId}/progress`)
            .then(response => response.json())
            .then(data => {
                const progressFill = document.getElementById('progress-fill');
                const progressPercentage = document.getElementById('progress-percentage');
                progressFill.style.width = `${data.progress}%`;
                progressPercentage.textContent = `${data.progress}%`;
            });
    }
});