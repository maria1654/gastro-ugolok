document.addEventListener('DOMContentLoaded', async function() {
    const rid = document.getElementById('recipe-id').value;
    const isNew = document.getElementById('is-new').value === 'true';
    
    if (isNew) {
        addIngredient();
        addStage();
        return;
    }
    
    try {
        const response = await fetch(`/api/recipes/${rid}`);
        if (!response.ok) {
            throw new Error(`Ошибка загрузки рецепта: ${response.status}`);
        }
        
        const recipe = await response.json();
        console.log('Полученные данные:', recipe);
        
        if (recipe.name) {
            document.getElementById('name').value = recipe.name;
        }
        if (recipe.time) {
            document.getElementById('time').value = recipe.time;
        }
        
        if (recipe.ingredient && typeof recipe.ingredient === 'object') {
            const ingredientsContainer = document.getElementById('ingredients-container');
            Object.entries(recipe.ingredient).forEach(([name, amount]) => {
                const div = document.createElement('div');
                div.className = 'ingredient-item';
                div.innerHTML = `
                    <input type="text" id="ingredient-name" name="ingredient-name" value="${name}" required placeholder="Название">
                    <input type="text" id="ingredient-amount" name="ingredient-amount" value="${amount}" required placeholder="Количество">
                    <button class="ingredient-remove" type="button" onclick="this.parentElement.remove()">❌</button>
                `;
                ingredientsContainer.appendChild(div);
            });
        }
        
        if (recipe.stage && typeof recipe.stage === 'object') {
            const stagesContainer = document.getElementById('stages-container');
            Object.entries(recipe.stage)
                .sort((a, b) => {
                    const numA = parseInt(a[0].split('_')[1]);
                    const numB = parseInt(b[0].split('_')[1]);
                    return numA - numB;
                })
                .forEach(([key, text], index) => {
                    const div = document.createElement('div');
                    div.className = 'stage-item';
                    div.innerHTML = `
                        <div class="stage-number">${index + 1}</div>
                        <textarea name="stage" required>${text}</textarea>
                        <button class="stage-remove" type="button" onclick="this.parentElement.remove()">❌</button>
                    `;
                    stagesContainer.appendChild(div);
                });
        }
    } catch (error) {
        console.error('Ошибка при загрузке:', error);
        if (!isNew) {
            alert(`Ошибка при загрузке рецепта: ${error.message}`);
        }
    }
});

function addIngredient() {
    const container = document.getElementById('ingredients-container');
    const div = document.createElement('div');
    div.className = 'ingredient-item';
    div.innerHTML = `
        <input type="text" id="ingredient-name" name="ingredient-name" placeholder="Например: Малина" required>
        <input type="text" id="ingredient-amount" name="ingredient-amount" placeholder="Например: 300 г" required>
        <button class="ingredient-remove" type="button" onclick="this.parentElement.remove()">❌</button>
    `;
    container.appendChild(div);
}

function addStage() {
    const container = document.getElementById('stages-container');
    const stageNumber = container.children.length + 1;
    const div = document.createElement('div');
    div.className = 'stage-item';
    div.innerHTML = `
        <div class="stage-number">${stageNumber}</div>
        <textarea name="stage" placeholder="Опишите этап приготовления" required></textarea>
        <button class="stage-remove" type="button" onclick="this.parentElement.remove()">❌</button>
    `;
    container.appendChild(div);
}

function getIngredients() {
    const ingredients = {};
    document.querySelectorAll('.ingredient-item').forEach(item => {
        const name = item.querySelector('[name="ingredient-name"]').value;
        const amount = item.querySelector('[name="ingredient-amount"]').value;
        if (name && amount) {
            ingredients[name] = amount;
        }
    });
    return ingredients;
}

function getStages() {
    const stages = {};
    document.querySelectorAll('.stage-item').forEach((item, index) => {
        const text = item.querySelector('textarea').value;
        if (text) {
            stages[`stage_${index + 1}`] = text;
        }
    });
    return stages;
}

document.getElementById('recipe-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const isNew = document.getElementById('is-new').value === 'true';
    const recipeData = {
        name: document.getElementById('name').value,
        time: document.getElementById('time').value,
        ingredients: getIngredients(),
        stages: getStages()
    };

    if (!isNew) {
        recipeData.rid = document.getElementById('recipe-id').value;
    }

    try {
        const endpoint = isNew ? '/admin/recipe/create' : '/admin/recipe/edit/save';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(recipeData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.status === 'success') {
            alert('Рецепт успешно сохранен!');
            window.location.href = `/recipe?rid=${result.rid}`;
        } else {
            alert('Ошибка при сохранении рецепта: ' + result.message);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при сохранении: ' + error.message);
    }
});

document.getElementById('image-upload').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        alert('Пожалуйста, выберите изображение');
        return;
    }

    const formData = new FormData();
    formData.append('image', file);
    formData.append('rid', document.getElementById('recipe-id').value);

    try {
        const response = await fetch('/admin/recipe/upload-image', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById('recipe-image').src = 
                `/recipes/${document.getElementById('recipe-id').value}/title.jpg?t=${Date.now()}`;
            alert('Изображение успешно загружено');
        } else {
            throw new Error('Ошибка при загрузке изображения');
        }
    } catch (error) {
        alert(`Ошибка при загрузке изображения: ${error.message}`);
    }
});

document.getElementById('image-upload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('recipe-image').src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

function deleteRecipe() {
    const recipeId = document.getElementById('recipe-id').value;
    
    const showAlert = window.showCustomAlert || window.alert;
    const showConfirm = window.showCustomConfirm || function(message, onConfirm) {
        if (window.confirm(message)) {
            onConfirm();
        }
    };
    
    showConfirm(
        'Вы уверены, что хотите удалить этот рецепт? Это действие нельзя отменить.',
        function() {
            fetch(`/admin/recipe/${recipeId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include'
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/catalog';
                } else {
                    showAlert('Ошибка при удалении рецепта');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Произошла ошибка при удалении рецепта');
            });
        }
    );
}
