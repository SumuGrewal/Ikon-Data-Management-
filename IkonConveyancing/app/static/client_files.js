document.addEventListener('DOMContentLoaded', () => {
    const fileEntriesContainer = document.querySelector('.file-entries');
    const detailsContent = document.querySelector('.details-content');
    const fileUpload = document.getElementById('file-upload');
    const saveDetailsButton = document.getElementById('save-details');
    const addClientButton = document.getElementById('add-client-button');
    const addClientPopup = document.getElementById('add-client-popup');
    const cancelButton = document.getElementById('cancel-button');
    const addClientForm = document.getElementById('add-client-form');

    function fetchClientFiles() {
        fetch('/api/client_files')
            .then(response => response.json())
            .then(data => {
                fileEntriesContainer.innerHTML = '';
                data.forEach(file => {
                    const fileEntry = document.createElement('div');
                    fileEntry.classList.add('file-entry');
                    fileEntry.setAttribute('data-file-number', file.file_number);
                    fileEntry.setAttribute('data-status', file.status);
                    fileEntry.innerHTML = `
                        <span>File Number: ${file.file_number}</span>
                        <span>Client Name: ${file.client_name}</span>
                        <span>Address: ${file.address}</span>
                        <span>Status: ${file.status}</span>
                        <span>Settlement Date: ${file.settlement_date}</span>
                    `;
                    fileEntriesContainer.appendChild(fileEntry);

                    fileEntry.addEventListener('click', () => {
                        // Load file details into the details-content container
                        detailsContent.innerHTML = `
                            <p>File Number: <span contenteditable="true">${file.file_number}</span></p>
                            <p>Client Name: <span contenteditable="true">${file.client_name}</span></p>
                            <p>Address: <span contenteditable="true">${file.address}</span></p>
                            <p>Status: <span contenteditable="true">${file.status}</span></p>
                            <p>Settlement Date: <span contenteditable="true">${file.settlement_date}</span></p>
                        `;

                        // Clear previous file upload
                        fileUpload.value = '';
                    });
                });
            })
            .catch(error => console.error('Error fetching client files:', error));
    }

    saveDetailsButton.addEventListener('click', () => {
        // Save the edited details and handle file upload
        const editedDetails = {
            fileNumber: detailsContent.querySelector('p:nth-child(1) span').innerText,
            clientName: detailsContent.querySelector('p:nth-child(2) span').innerText,
            address: detailsContent.querySelector('p:nth-child(3) span').innerText,
            status: detailsContent.querySelector('p:nth-child(4) span').innerText,
            settlementDate: detailsContent.querySelector('p:nth-child(5) span').innerText,
        };

        const file = fileUpload.files[0];
        if (file) {
            // Handle file upload
            const formData = new FormData();
            formData.append('file', file);
            formData.append('fileNumber', editedDetails.fileNumber);

            fetch('/upload', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                console.log('File uploaded successfully:', data);
            })
            .catch(error => {
                console.error('Error uploading file:', error);
            });
        }

        // Save the edited details (this is just a placeholder, you need to implement the actual save logic)
        console.log('Edited details:', editedDetails);
    });

    addClientButton.addEventListener('click', () => {
        addClientPopup.style.display = 'block';
    });

    cancelButton.addEventListener('click', () => {
        addClientPopup.style.display = 'none';
    });

    addClientForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(addClientForm);
        const data = Object.fromEntries(formData.entries());

        fetch('/api/client_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.message === 'Client file added successfully') {
                fetchClientFiles();
                addClientPopup.style.display = 'none';
                addClientForm.reset();
            } else {
                console.error('Error adding client file:', result.message);
            }
        })
        .catch(error => console.error('Error adding client file:', error));
    });

    // Optional: Close the popup when clicking outside of it
    window.addEventListener('click', (event) => {
        if (event.target == addClientPopup) {
            addClientPopup.style.display = 'none';
        }
    });

    // Fetch client files on page load
    fetchClientFiles();
});