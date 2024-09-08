document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('addClientModal');
    const btn = document.getElementById('add-client');
    const span = document.getElementsByClassName('close')[0];
    const form = document.getElementById('add-client-form');

    // Open the modal
    btn.onclick = function() {
        modal.style.display = 'block';
    }

    // Close the modal
    span.onclick = function() {
        modal.style.display = 'none';
    }

    // Close the modal when clicking outside of it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    // Handle form submission
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const fileNumber = document.getElementById('file-number').value;
        const clientName = document.getElementById('client-name').value;
        const address = document.getElementById('address').value;
        const status = document.getElementById('status').value;
        const settlementDate = document.getElementById('settlement-date').value;

        fetch('/api/client_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_number: fileNumber,
                client_name: clientName,
                address: address,
                status: status,
                settlement_date: settlementDate
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === 'Client file added successfully') {
                // Create a new file entry element
                const newFileEntry = document.createElement('div');
                newFileEntry.classList.add('file-entry');
                newFileEntry.setAttribute('data-file-number', fileNumber);
                newFileEntry.setAttribute('data-status', status);

                newFileEntry.innerHTML = `
                    <span>File Number: ${fileNumber}</span>
                    <span>Client Name: ${clientName}</span>
                    <span>Address: ${address}</span>
                    <span>Status: ${status}</span>
                    <span>Settlement Date: ${settlementDate}</span>
                `;

                // Append the new file entry to the file entries container
                document.querySelector('.file-entries').appendChild(newFileEntry);

                // Close the modal
                modal.style.display = 'none';

                // Reset the form
                form.reset();
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error adding client file');
        });
    });
});