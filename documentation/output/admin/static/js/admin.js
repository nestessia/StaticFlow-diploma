// Admin panel functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add active class to current nav item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Handle settings form submission
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(settingsForm);
            const settings = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('/admin/api/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settings)
                });
                
                if (!response.ok) {
                    throw new Error('Failed to save settings');
                }
                
                alert('Settings saved successfully!');
            } catch (error) {
                alert('Error saving settings: ' + error.message);
            }
        });
    }
});

// Content management functions
async function createContent() {
    const path = prompt('Enter content path (e.g., posts/new-post.md):');
    if (!path) return;
    
    try {
        const response = await fetch('/admin/api/content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'create',
                path: path,
                content: '---\ntitle: New Content\n---\n\nWrite your content here...'
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to create content');
        }
        
        window.location.reload();
    } catch (error) {
        alert('Error creating content: ' + error.message);
    }
}

async function editContent(path) {
    window.location.href = `/admin/content/edit?path=${encodeURIComponent(path)}`;
} 