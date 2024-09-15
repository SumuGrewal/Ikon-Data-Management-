document.addEventListener('DOMContentLoaded', function() {
    const fileList = document.getElementById('file-list');
    const checklistItems = document.getElementById('checklist-items');
    const selectedFile = document.getElementById('selected-file');
    const progressBar = document.getElementById('progress-bar');
    const progressFill = document.getElementById('progress-fill');
    const progressPercentage = document.getElementById('progress-percentage');

    // Fetch and display the list of files
    fetch('/api/client_files')
        .then(response => response.json())
        .then(files => {
            files.forEach(file => {
                const li = document.createElement('li');
                li.textContent = file.file_number;
                li.addEventListener('click', () => loadChecklist(file.id, file.file_number));
                fileList.appendChild(li);
            });
        });

    // Load checklist for the selected file
    function loadChecklist(fileId, fileNumber) {
        selectedFile.textContent = fileNumber;
        checklistItems.innerHTML = '';
        fetch(`/api/checklist/${fileId}`)
            .then(response => response.json())
            .then(items => {
                items.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item.description;
                    li.addEventListener('click', () => displayItemDetails(item));
                    checklistItems.appendChild(li);
                });
                updateProgress(fileId);
            });
    }

    // Display checklist item details
    function displayItemDetails(item) {
        alert(`Details for item: ${item.description}\nStatus: ${item.status}`);
    }

    // Update progress bar
    function updateProgress(fileId) {
        fetch(`/api/checklist/${fileId}/progress`)
            .then(response => response.json())
            .then(data => {
                progressFill.style.width = `${data.progress}%`;
                progressPercentage.textContent = `${data.progress}%`;
            });
    }

    // Display progress details
    progressBar.addEventListener('click', () => {
        alert(`Progress details: ${progressPercentage.textContent}`);
    });
});