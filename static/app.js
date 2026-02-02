/**
 * AI Ad Generator - Frontend Application
 */

// State
let products = [];
let currentJobId = null;
let pollInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Add first product by default
    addProduct();
});

/**
 * Add a new product card
 */
function addProduct() {
    if (products.length >= 7) {
        alert('Maximum 7 products allowed per batch');
        return;
    }

    const productId = Date.now();
    products.push({
        id: productId,
        name: '',
        description: '',
        guidance: '',
        includeProduct: true
    });

    renderProducts();
}

/**
 * Remove a product card
 */
function removeProduct(productId) {
    if (products.length <= 1) {
        alert('You need at least one product');
        return;
    }

    products = products.filter(p => p.id !== productId);
    renderProducts();
}

/**
 * Render all product cards
 */
function renderProducts() {
    const container = document.getElementById('products-container');

    container.innerHTML = products.map((product, index) => `
        <div class="product-card fade-in" data-product-id="${product.id}">
            <div class="product-card-header">
                <div class="product-number">
                    <span class="number">${index + 1}</span>
                    <span>Product</span>
                </div>
                ${products.length > 1 ? `
                    <button class="remove-btn" onclick="removeProduct(${product.id})" title="Remove">
                        ✕
                    </button>
                ` : ''}
            </div>
            
            <div class="product-fields">
                <div class="field-row">
                    <div class="field-group">
                        <label>Product Name</label>
                        <input 
                            type="text" 
                            placeholder="e.g., Anti-Aging Serum"
                            value="${escapeHtml(product.name)}"
                            onchange="updateProduct(${product.id}, 'name', this.value)"
                        >
                    </div>
                    <div class="field-group">
                        <label class="checkbox-group">
                            <input 
                                type="checkbox" 
                                ${product.includeProduct ? 'checked' : ''}
                                onchange="updateProduct(${product.id}, 'includeProduct', this.checked)"
                            >
                            Show product in image
                        </label>
                    </div>
                </div>
                
                <div class="field-group full-width">
                    <label>Product Description / Brief</label>
                    <textarea 
                        placeholder="Describe the product, its benefits, target audience, and key selling points. The more detail, the better the ads!"
                        onchange="updateProduct(${product.id}, 'description', this.value)"
                    >${escapeHtml(product.description)}</textarea>
                </div>
                
                <div class="field-group full-width">
                    <label>Creative Guidance (Optional)</label>
                    <textarea 
                        placeholder="Any specific direction? e.g., 'Push anti-aging angle', 'Focus on dirty carpet disgust', 'Lifestyle shots in office setting'"
                        onchange="updateProduct(${product.id}, 'guidance', this.value)"
                    >${escapeHtml(product.guidance)}</textarea>
                </div>
            </div>
        </div>
    `).join('');

    // Update add button state
    const addBtn = document.getElementById('add-product-btn');
    if (products.length >= 7) {
        addBtn.disabled = true;
        addBtn.textContent = 'Maximum 7 Products';
    } else {
        addBtn.disabled = false;
        addBtn.innerHTML = '<span class="btn-icon">+</span> Add Product';
    }
}

/**
 * Update a product field
 */
function updateProduct(productId, field, value) {
    const product = products.find(p => p.id === productId);
    if (product) {
        product[field] = value;
    }
}

/**
 * Start the generation process
 */
async function startGeneration() {
    // Validate products
    const validProducts = products.filter(p => p.name.trim() && p.description.trim());

    if (validProducts.length === 0) {
        alert('Please add at least one product with a name and description');
        return;
    }

    // Get settings
    const adSize = document.getElementById('ad-size').value;
    const headlinesCount = parseInt(document.getElementById('headlines-count').value);
    const imagesCount = parseInt(document.getElementById('images-count').value);

    // Prepare request
    const request = {
        products: validProducts.map(p => ({
            name: p.name,
            description: p.description,
            guidance: p.guidance || null,
            include_product: p.includeProduct
        })),
        headlines_per_product: headlinesCount,
        images_per_product: imagesCount,
        ad_size: adSize
    };

    // Show progress section
    document.getElementById('input-section').classList.add('hidden');
    document.getElementById('progress-section').classList.remove('hidden');
    document.getElementById('results-section').classList.add('hidden');

    try {
        // Start generation job
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error('Failed to start generation');
        }

        const job = await response.json();
        currentJobId = job.job_id;

        // Start polling for status
        pollInterval = setInterval(() => pollJobStatus(), 2000);

    } catch (error) {
        console.error('Error starting generation:', error);
        alert('Failed to start generation: ' + error.message);
        showInputSection();
    }
}

/**
 * Poll for job status
 */
async function pollJobStatus() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`/api/jobs/${currentJobId}`);
        if (!response.ok) throw new Error('Failed to get job status');

        const job = await response.json();

        // Update progress UI
        updateProgress(job.progress, job.message);

        // Check if completed or failed
        if (job.status === 'completed') {
            clearInterval(pollInterval);
            showResults(job.result);
        } else if (job.status === 'failed') {
            clearInterval(pollInterval);
            alert('Generation failed: ' + job.message);
            showInputSection();
        }

    } catch (error) {
        console.error('Error polling status:', error);
    }
}

/**
 * Update progress UI
 */
function updateProgress(percent, message) {
    document.getElementById('progress-percent').textContent = `${Math.round(percent)}%`;
    document.getElementById('progress-bar').style.width = `${percent}%`;
    document.getElementById('progress-message').textContent = message;
}

/**
 * Show results section
 */
function showResults(result) {
    document.getElementById('input-section').classList.add('hidden');
    document.getElementById('progress-section').classList.add('hidden');
    document.getElementById('results-section').classList.remove('hidden');

    const grid = document.getElementById('results-grid');

    if (!result || !result.products) {
        grid.innerHTML = '<p>No results found</p>';
        return;
    }

    grid.innerHTML = result.products.map(product => {
        if (product.error) {
            return `
                <div class="result-product">
                    <div class="result-product-header">
                        <h3>❌ ${escapeHtml(product.product_name)}</h3>
                        <p>Error: ${escapeHtml(product.error)}</p>
                    </div>
                </div>
            `;
        }

        const headlines = product.headlines || [];
        const ads = product.final_ads || [];

        return `
            <div class="result-product fade-in">
                <div class="result-product-header">
                    <h3>📦 ${escapeHtml(product.product_name)}</h3>
                    <p>${ads.length} ads generated</p>
                </div>
                
                <div class="result-headlines" style="padding: 16px; border-bottom: 1px solid var(--border-color);">
                    <p style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 8px;">Headlines:</p>
                    ${headlines.map(h => `
                        <p style="font-weight: 500; margin-bottom: 4px;">"${escapeHtml(h.text)}"</p>
                    `).join('')}
                </div>
                
                <div class="result-ads-grid">
                    ${ads.map((adPath, i) => {
            const filename = adPath.split('/').pop();
            return `
                            <div class="result-ad" onclick="openImage('/api/output/${filename}')">
                                <img src="/api/output/${filename}" alt="Ad ${i + 1}" loading="lazy">
                                <div class="result-ad-overlay">
                                    <button onclick="event.stopPropagation(); downloadImage('/api/output/${filename}', '${filename}')">
                                        Download
                                    </button>
                                </div>
                            </div>
                        `;
        }).join('')}
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Show input section
 */
function showInputSection() {
    document.getElementById('input-section').classList.remove('hidden');
    document.getElementById('progress-section').classList.add('hidden');
    document.getElementById('results-section').classList.add('hidden');
    currentJobId = null;
}

/**
 * Start over
 */
function startOver() {
    currentJobId = null;
    products = [];
    addProduct();
    showInputSection();
}

/**
 * Download all ads as ZIP
 */
async function downloadAll() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`/api/download-batch/${currentJobId}`);
        if (!response.ok) throw new Error('Failed to download');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ads_batch_${currentJobId.substring(0, 8)}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error('Error downloading:', error);
        alert('Failed to download: ' + error.message);
    }
}

/**
 * Open image in new tab
 */
function openImage(url) {
    window.open(url, '_blank');
}

/**
 * Download single image
 */
async function downloadImage(url, filename) {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
        console.error('Error downloading image:', error);
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
