document.addEventListener('DOMContentLoaded', function() {
    const addClientButton = document.getElementById('add-client-button');
    const addClientPopup = document.getElementById('add-client-popup');
    const addClientForm = document.getElementById('add-client-form');
    const fileEntriesContainer = document.querySelector('.file-entries');

    // Show the add client popup
    addClientButton.addEventListener('click', () => {
        addClientPopup.style.display = 'block';
    });

    // Hide the add client popup
    document.getElementById('cancel-button').addEventListener('click', () => {
        addClientPopup.style.display = 'none';
    });

    // Handle form submission
    addClientForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(addClientForm);
        const data = {
            file_number: formData.get('file-number'),
            client_name: formData.get('client-name'),
            address: formData.get('address'),
            status: formData.get('status'),
            settlement_date: formData.get('settlement-date')
        };

        try {
            const response = await fetch('/api/client_files', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                console.log(result.message);
                addClientPopup.style.display = 'none';
                addClientForm.reset();
                fetchClientFiles(); // Fetch and display the updated list of client files
            } else {
                const error = await response.json();
                console.error(error.message);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Fetch and display client files
    async function fetchClientFiles() {
        try {
            const response = await fetch('/api/client_files');
            const clientFiles = await response.json();

            // Clear the existing entries
            fileEntriesContainer.innerHTML = '';

            // Populate the container with the updated client files
            clientFiles.forEach(file => {
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
                `;

                fileEntriesContainer.appendChild(fileEntry);
            });
        } catch (error) {
            console.error('Error fetching client files:', error);
        }
    }

    // Initial fetch of client files
    fetchClientFiles();
});