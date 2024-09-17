document.addEventListener('DOMContentLoaded', function() {
    const templateForm = document.getElementById('template-form');
    const subjectInput = document.getElementById('subject');
    const bodyInput = document.getElementById('body');
    const templateList = document.querySelector('.template-list');
    const templateFormContainer = document.getElementById('template-form-container');
    const newTemplateBtn = document.getElementById('new-template');
    const cancelFormBtn = document.getElementById('cancel-form');

    let editingTemplateId = null;

    // Load existing templates
    fetch('/api/templates')
        .then(response => response.json())
        .then(data => {
            data.forEach(template => addTemplateToList(template));
        });

    // Handle form submission
    templateForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const subject = subjectInput.value;
        const body = bodyInput.value;

        const url = editingTemplateId ? `/api/templates/${editingTemplateId}` : '/api/templates';
        const method = editingTemplateId ? 'PUT' : 'POST';

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ subject, body }),
        })
        .then(response => response.json())
        .then(data => {
            if (editingTemplateId) {
                updateTemplateInList(data);
            } else {
                addTemplateToList(data);
            }
            templateFormContainer.style.display = 'none';
            templateForm.reset();
            editingTemplateId = null;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    // Handle new template button click
    newTemplateBtn.addEventListener('click', function() {
        templateFormContainer.style.display = 'block';
        templateForm.reset();
        editingTemplateId = null;
    });

    // Handle cancel button click
    cancelFormBtn.addEventListener('click', function() {
        templateFormContainer.style.display = 'none';
        templateForm.reset();
        editingTemplateId = null;
    });

    // Function to add a new template to the list
    function addTemplateToList(template) {
        const li = document.createElement('li');
        li.textContent = template.subject;
        li.dataset.id = template.id;

        const editBtn = document.createElement('button');
        editBtn.textContent = 'Edit';
        editBtn.addEventListener('click', () => editTemplate(template));

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.addEventListener('click', () => deleteTemplate(template.id));

        li.appendChild(editBtn);
        li.appendChild(deleteBtn);
        templateList.appendChild(li);
    }

    // Function to update a template in the list
    function updateTemplateInList(template) {
        const li = document.querySelector(`li[data-id='${template.id}']`);
        li.textContent = template.subject;

        const editBtn = document.createElement('button');
        editBtn.textContent = 'Edit';
        editBtn.addEventListener('click', () => editTemplate(template));

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.addEventListener('click', () => deleteTemplate(template.id));

        li.appendChild(editBtn);
        li.appendChild(deleteBtn);
    }

    // Function to edit a template
    function editTemplate(template) {
        templateFormContainer.style.display = 'block';
        subjectInput.value = template.subject;
        bodyInput.value = template.body;
        editingTemplateId = template.id;
    }

    // Function to delete a template
    function deleteTemplate(id) {
        fetch(`/api/templates/${id}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            document.querySelector(`li[data-id='${id}']`).remove();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }
});