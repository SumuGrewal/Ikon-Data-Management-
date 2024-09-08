document.addEventListener('DOMContentLoaded', () => {
    const fileEntries = document.querySelectorAll('.file-entry');
    const detailsContent = document.querySelector('.details-content');
    const fileUpload = document.getElementById('file-upload');
    const saveDetailsButton = document.getElementById('save-details');

    fileEntries.forEach(entry => {
        entry.addEventListener('click', () => {
            // Load file details into the details-content container
            const fileNumber = entry.getAttribute('data-file-number');
            const clientName = entry.querySelector('span:nth-child(2)').innerText;
            const address = entry.querySelector('span:nth-child(3)').innerText;
            const status = entry.querySelector('span:nth-child(4)').innerText;
            const settlementDate = entry.querySelector('span:nth-child(5)').innerText;

            detailsContent.innerHTML = `
                <p>File Number: <span contenteditable="true">${fileNumber}</span></p>
                <p>Client Name: <span contenteditable="true">${clientName}</span></p>
                <p>Address: <span contenteditable="true">${address}</span></p>
                <p>Status: <span contenteditable="true">${status}</span></p>
                <p>Settlement Date: <span contenteditable="true">${settlementDate}</span></p>
            `;

            // Clear previous file upload
            fileUpload.value = '';
        });
    });

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
});