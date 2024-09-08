document.addEventListener('DOMContentLoaded', function() {
    const addClientButton = document.getElementById('add-client-button');
    const addClientPopup = document.getElementById('add-client-popup');
    const addClientForm = document.getElementById('add-client-form');
    const cancelButton = document.getElementById('cancel-button');

    addClientButton.addEventListener('click', function() {
        addClientPopup.style.display = 'block';
    });

    cancelButton.addEventListener('click', function() {
        addClientPopup.style.display = 'none';
        addClientForm.reset();
    });

    addClientForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData(addClientForm);
        const clientData = Object.fromEntries(formData.entries());

        fetch('/api/client_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(clientData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const newEntry = createClientEntry(clientData);
                document.querySelector('.file-entries').appendChild(newEntry);
                addClientPopup.style.display = 'none';
                addClientForm.reset();
            } else {
                alert('Error adding client: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while adding the client.');
        });
    });

    function createClientEntry(clientData) {
        const newEntry = document.createElement('div');
        newEntry.classList.add('file-entry');
        newEntry.dataset.fileNumber = clientData['file-number'];
        newEntry.dataset.status = clientData.status;
        newEntry.innerHTML = `
            <span>File Number: ${clientData['file-number']}</span>
            <span>Client Name: ${clientData['client-name']}</span>
            <span>Address: ${clientData.address}</span>
            <span>Status: ${clientData.status}</span>
            <span>Settlement Date: ${clientData['settlement-date']}</span>
        `;
        return newEntry;
    }

    // ... (keep the existing code for filters and other functionality)
});