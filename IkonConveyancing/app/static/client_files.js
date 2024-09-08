// /IkonConveyancing/app/static/client_files.js

document.addEventListener('DOMContentLoaded', function() {
    loadClientFiles();

    document.getElementById('save-details').addEventListener('click', function() {
        const detailsContent = document.querySelector('.details-content').innerText;
        const fileNumber = document.querySelector('.file-entry.active').dataset.fileNumber;
        saveClientFileDetails(fileNumber, detailsContent);
    });
});

function loadClientFiles() {
    fetch('/api/client_files')
        .then(response => response.json())
        .then(files => {
            const fileEntries = document.getElementById('file-entries');
            fileEntries.innerHTML = '';
            files.forEach(file => {
                const fileEntry = document.createElement('div');
                fileEntry.classList.add('file-entry');
                fileEntry.dataset.fileNumber = file.file_number;
                fileEntry.dataset.status = file.status;
                fileEntry.innerHTML = `
                    <span>File Number: ${file.file_number}</span>
                    <span>Client Name: ${file.client_name}</span>
                    <span>Address: ${file.address}</span>
                    <span>Status: ${file.status}</span>
                    <span>Settlement Date: ${file.settlement_date}</span>
                    <button class="delete-button" onclick="deleteClientFile('${file.file_number}')">Delete</button>
                `;
                fileEntry.addEventListener('click', function() {
                    loadClientFileDetails(file.file_number);
                });
                fileEntries.appendChild(fileEntry);
            });
        })
        .catch(error => console.error('Error:', error));
}

function loadClientFileDetails(fileNumber) {
    fetch(`/client_files/${fileNumber}`)
        .then(response => response.json())
        .then(file => {
            const detailsContent = document.querySelector('.details-content');
            detailsContent.innerText = file.notes || '';
            document.querySelectorAll('.file-entry').forEach(entry => entry.classList.remove('active'));
            document.querySelector(`.file-entry[data-file-number="${fileNumber}"]`).classList.add('active');
        })
        .catch(error => console.error('Error:', error));
}

function saveClientFileDetails(fileNumber, detailsContent) {
    fetch(`/api/client_files/${fileNumber}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notes: detailsContent })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Client file updated successfully') {
            alert('Details saved successfully');
        } else {
            alert('Error saving details: ' + data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}