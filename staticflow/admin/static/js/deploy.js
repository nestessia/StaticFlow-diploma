/**
 * Deployment functionality for StaticFlow Admin
 */

document.addEventListener('DOMContentLoaded', function() {
    // Безопасное получение элементов с проверкой на null
    const deployBtn = document.getElementById('deploy-btn');
    const deployForm = document.getElementById('github-pages-form');
    const statusMsg = document.getElementById('deploy-status-msg');
    const lastDeploymentTime = document.getElementById('last-deployment-time');
    const historyTableElement = document.getElementById('history-table');
    const historyTable = historyTableElement ? historyTableElement.querySelector('tbody') : null;
    const commitMessageInput = document.getElementById('commit-message');
    
    // Находим все поля формы, чтобы обновить их значения
    const repoUrlInput = document.getElementById('repo-url');
    const branchInput = document.getElementById('branch');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const tokenInput = document.getElementById('token');
    const cnameInput = document.getElementById('cname');
    
    // Загружаем свежие данные при открытии страницы
    loadFreshConfigData();
    
    /**
     * Загружает свежие данные конфигурации с сервера
     */
    async function loadFreshConfigData() {
        try {
            const response = await fetch('/admin/api/deploy/config?' + new Date().getTime(), {
                method: 'GET',
                headers: {
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Обновляем поля формы с полученными данными
            if (data.config) {
                if (repoUrlInput) repoUrlInput.value = data.config.repo_url || '';
                if (branchInput) branchInput.value = data.config.branch || '';
                if (usernameInput) usernameInput.value = data.config.username || '';
                if (emailInput) emailInput.value = data.config.email || '';
                if (tokenInput) tokenInput.value = data.config.has_token ? 'STORED_TOKEN' : '';
                if (cnameInput) cnameInput.value = data.config.cname || '';
            }
            
            // Обновляем статус и историю развертывания
            if (data.status) {
                // Обновляем статус конфигурации
                if (statusMsg) {
                    statusMsg.textContent = data.status.configured ? 'Configuration ready' : 'Not configured';
                }
                
                // Обновляем кнопку Deploy
                if (deployBtn) {
                    deployBtn.disabled = !data.status.configured;
                }
                
                // Обновляем время последнего развертывания
                if (lastDeploymentTime && data.status.last_deployment) {
                    lastDeploymentTime.textContent = formatDate(data.status.last_deployment);
                }
                
                // Обновляем историю развертывания
                if (data.status.history && historyTable) {
                    updateHistoryTableFull(data.status.history);
                }
            }
        } catch (error) {
            console.error('Error loading fresh configuration data:', error);
        }
    }
    
    /**
     * Полностью обновляет таблицу истории развертывания
     * @param {Array} history - Полная история развертывания
     */
    function updateHistoryTableFull(history) {
        if (!historyTable) return;
        
        try {
            // Очищаем таблицу
            historyTable.innerHTML = '';
            
            if (!history || history.length === 0) {
                // Если история пуста, показываем сообщение
                const row = document.createElement('tr');
                row.innerHTML = '<td colspan="2">No deployment history available</td>';
                historyTable.appendChild(row);
                return;
            }
            
            // Добавляем каждую запись из истории
            history.forEach(deployment => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${formatDate(deployment.timestamp)}</td>
                    <td><span class="status-badge status-${deployment.status}">${deployment.status}</span></td>
                `;
                historyTable.appendChild(row);
            });
        } catch (e) {
            console.error('Error updating history table full:', e);
        }
    }
    
    /**
     * Format date for display
     * @param {string} dateString - ISO date string
     * @returns {string} - Formatted date string
     */
    function formatDate(dateString) {
        if (!dateString) return 'Never';
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch (e) {
            console.error('Error formatting date:', e);
            return dateString || 'Unknown';
        }
    }
    
    // Безопасный селектор с проверкой на null
    try {
        const firstCells = document.querySelectorAll('#history-table tbody td:first-child');
        if (firstCells && firstCells.length > 0) {
            firstCells.forEach(cell => {
                if (cell) {
                    cell.textContent = formatDate(cell.textContent);
                }
            });
        }
    } catch (e) {
        console.error('Error formatting history dates:', e);
    }
    
    // Handle form submission
    if (deployForm) {
        deployForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Handle deploy button click
    if (deployBtn) {
        deployBtn.addEventListener('click', handleDeploy);
    }
    
    /**
     * Handle form submission
     * @param {Event} e - Submit event
     */
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        try {
            const formData = new FormData(deployForm);
            const configData = {};
            
            formData.forEach((value, key) => {
                // Don't send empty token (keep existing)
                if (key === 'token' && (value === 'STORED_TOKEN' || !value)) {
                    return;
                }
                configData[key] = value;
            });
            
            // Show saving status - с проверкой на null
            const submitBtn = deployForm.querySelector('button[type="submit"]');
            if (!submitBtn) {
                console.error('Submit button not found');
                return;
            }
            
            const originalBtnText = submitBtn.textContent || 'Save Configuration';
            submitBtn.innerHTML = '<span class="spinner"></span> Saving...';
            submitBtn.disabled = true;
            
            try {
                const response = await fetch('/admin/api/deploy/config', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0'
                    },
                    body: JSON.stringify(configData)
                });
                
                if (!response.ok) {
                    throw new Error(`Server responded with status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    alert('Configuration saved successfully');
                    
                    // Enable deploy button if config is valid
                    if (data.is_valid && deployBtn) {
                        deployBtn.disabled = false;
                        if (statusMsg) statusMsg.textContent = 'Configuration ready';
                    } else if (statusMsg) {
                        statusMsg.textContent = 'Configuration incomplete';
                    }
                    
                    // Check for warnings
                    if (data.warnings && data.warnings.length > 0) {
                        alert('Warning: ' + data.warnings.join('\n'));
                    }
                    
                    // Сразу загружаем свежие данные
                    loadFreshConfigData();
                } else {
                    alert('Error saving configuration: ' + (data.message || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error saving configuration:', error);
                alert('Error saving configuration: ' + error.message);
            } finally {
                // Restore button
                if (submitBtn) {
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                }
            }
        } catch (e) {
            console.error('Error in form submission:', e);
            alert('An unexpected error occurred: ' + e.message);
        }
    }
    
    /**
     * Handle deploy button click
     */
    async function handleDeploy() {
        try {
            // Get commit message if provided
            const commitMessage = commitMessageInput && commitMessageInput.value ? commitMessageInput.value.trim() : '';
            
            // Change button to loading state
            const originalBtnText = deployBtn.textContent || 'Deploy to GitHub Pages';
            deployBtn.innerHTML = '<span class="spinner"></span> Deploying...';
            deployBtn.disabled = true;
            
            // Безопасное обновление статуса
            if (statusMsg) {
                statusMsg.textContent = 'Deployment in progress...';
            }
            
            try {
                const response = await fetch('/admin/api/deploy/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0'
                    },
                    body: JSON.stringify({
                        commit_message: commitMessage
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`Server responded with status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success) {
                    // Update status message
                    if (statusMsg) {
                        statusMsg.textContent = 'Deployment successful!';
                    }
                    
                    // Update last deployment time - с проверкой на null
                    if (data.timestamp && lastDeploymentTime) {
                        lastDeploymentTime.textContent = formatDate(data.timestamp);
                    }
                    
                    // Update history table if it exists
                    updateHistoryTable(data.history);
                    
                    // Clear commit message field - с проверкой на null
                    if (commitMessageInput) {
                        commitMessageInput.value = '';
                    }
                    
                    alert('Site deployed successfully!');
                    
                    // Сразу загружаем свежие данные
                    loadFreshConfigData();
                } else {
                    if (statusMsg) {
                        statusMsg.textContent = 'Deployment failed';
                    }
                    alert('Error deploying site: ' + (data.message || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error deploying site:', error);
                if (statusMsg) {
                    statusMsg.textContent = 'Deployment failed';
                }
                alert('Error deploying site: ' + error.message);
            } finally {
                // Restore button - с проверкой на null
                if (deployBtn) {
                    deployBtn.innerHTML = originalBtnText;
                    deployBtn.disabled = false;
                }
            }
        } catch (e) {
            console.error('Error in deploy handler:', e);
            alert('An unexpected error occurred: ' + e.message);
            // Ensure button is restored even if there's an error
            if (deployBtn) {
                deployBtn.innerHTML = 'Deploy to GitHub Pages';
                deployBtn.disabled = false;
            }
        }
    }
    
    /**
     * Update history table with new deployment data
     * @param {Array} history - Deployment history array
     */
    function updateHistoryTable(history) {
        // Skip if history is missing or historyTable doesn't exist
        if (!history || !history.length || !historyTable) {
            return;
        }
        
        try {
            const latestDeployment = history[0];
            
            // Clear "no history" row if present
            const noHistoryRow = historyTable.querySelector('td[colspan="2"]');
            if (noHistoryRow) {
                historyTable.innerHTML = '';
            }
            
            // Create new row
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td>${formatDate(latestDeployment.timestamp)}</td>
                <td><span class="status-badge status-${latestDeployment.status}">${latestDeployment.status}</span></td>
            `;
            
            // Insert row at the beginning of the table
            if (historyTable.firstChild) {
                historyTable.insertBefore(newRow, historyTable.firstChild);
            } else {
                historyTable.appendChild(newRow);
            }
        } catch (e) {
            console.error('Error updating history table:', e);
        }
    }
}); 