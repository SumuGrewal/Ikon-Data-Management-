document.addEventListener('DOMContentLoaded', function() {
    const todoForm = document.getElementById('todo-form');
    const todoInput = document.getElementById('todo-input');
    const todoList = document.getElementById('todo-list');

    // Load existing to-do items
    fetch('/api/todos')
        .then(response => response.json())
        .then(data => {
            data.forEach(todo => addTodoToList(todo));
        });

    // Handle form submission
    todoForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const description = todoInput.value;

        fetch('/api/todos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description }),
        })
        .then(response => response.json())
        .then(data => {
            addTodoToList(data);
            todoInput.value = '';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    // Function to add a new to-do item to the list
    function addTodoToList(todo) {
        const li = document.createElement('li');
        li.textContent = todo.description;
        li.dataset.id = todo.id;

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.addEventListener('click', () => deleteTodoItem(todo.id));

        li.appendChild(deleteBtn);
        todoList.appendChild(li);
    }

    // Function to delete a to-do item
    function deleteTodoItem(id) {
        fetch(`/api/todos/${id}`, {
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