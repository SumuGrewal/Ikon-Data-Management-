document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const fileNumber = window.location.pathname.split('/').pop();

    fetch(`/api/client_files/${fileNumber}/upload`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'File uploaded successfully') {
            alert('File uploaded successfully');
        } else {
            alert('Error uploading file');
        }
    });
});