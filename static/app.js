/**
 * AdForge AI - Frontend Application
 * Modern ES6+ implementation with proper event handling
 */

// ============ State ============
const state = {
    products: [],
    currentJobId: null,
    pollInterval: null
};

// ============ DOM Elements ============
const elements = {};

// ============ Initialize ============
document.addEventListener('DOMContentLoaded', () => {
    console.log('AdForge AI initializing...');

    // Cache DOM elements
    cacheElements();

    // Setup event listeners
    setupEventListeners();

    // Add first product
    addProduct();

    // Update estimates
    updateEstimates();

    console.log('AdForge AI ready!');
});

function cacheElements() {
    elements.productsContainer = document.getElementById('products-container');
    elements.emptyState = document.getElementById('empty-state');
    elements.addProductBtn = document.getElementById('add-product-btn');
    elements.addFirstProductBtn = document.getElementById('add-first-product-btn');
    elements.generateBtn = document.getElementById('generate-btn');
    elements.downloadAllBtn = document.getElementById('download-all-btn');
    elements.startOverBtn = document.getElementById('start-over-btn');
    elements.inputSection = document.getElementById('input-section');
    elements.progressSection = document.getElementById('progress-section');
    elements.resultsSection = document.getElementById('results-section');
    elements.progressBar = document.getElementById('progress-bar');
    elements.progressPercent = document.getElementById('progress-percent');
    elements.progressMessage = document.getElementById('progress-message');
    elements.resultsGrid = document.getElementById('results-grid');
    elements.resultsCount = document.getElementById('results-count');
    elements.productCount = document.getElementById('product-count');
    elements.adEstimate = document.getElementById('ad-estimate');
    elements.outputEstimate = document.getElementById('output-estimate');
    elements.costEstimate = document.getElementById('cost-estimate');
    elements.headlinesCount = document.getElementById('headlines-count');
    elements.imagesCount = document.getElementById('images-count');
    elements.adSize = document.getElementById('ad-size');
}

function setupEventListeners() {
    // Add product buttons
    if (elements.addProductBtn) {
        elements.addProductBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Add product clicked');
            addProduct();
        });
    }

    if (elements.addFirstProductBtn) {
        elements.addFirstProductBtn.addEventListener('click', (e) => {
            e.preventDefault();
            addProduct();
        });
    }

    // Generate button
    if (elements.generateBtn) {
        elements.generateBtn.addEventListener('click', (e) => {
            e.preventDefault();
            startGeneration();
        });
    }

    // Download all button
    if (elements.downloadAllBtn) {
        elements.downloadAllBtn.addEventListener('click', (e) => {
            e.preventDefault();
            downloadAll();
        });
    }

    // Start over button
    if (elements.startOverBtn) {
        elements.startOverBtn.addEventListener('click', (e) => {
            e.preventDefault();
            startOver();
        });
    }

    // Settings change listeners
    if (elements.headlinesCount) {
        elements.headlinesCount.addEventListener('change', updateEstimates);
    }
    if (elements.imagesCount) {
        elements.imagesCount.addEventListener('change', updateEstimates);
    }
}

// ============ Product Management ============
function addProduct() {
    if (state.products.length >= 7) {
        showNotification('Maximum 7 products allowed per batch', 'warning');
        return;
    }

    const productId = Date.now();
    state.products.push({
        id: productId,
        name: '',
        description: '',
        guidance: '',
        includeProduct: true
    });

    renderProducts();
    updateEstimates();

    // Focus the new product's name input
    setTimeout(() => {
        const newInput = document.querySelector(`[data-product-id="${productId}"] .field-input`);
        if (newInput) newInput.focus();
    }, 100);
}

function removeProduct(productId) {
    if (state.products.length <= 1) {
        showNotification('You need at least one product', 'warning');
        return;
    }

    state.products = state.products.filter(p => p.id !== productId);
    renderProducts();
    updateEstimates();
}

function updateProduct(productId, field, value) {
    const product = state.products.find(p => p.id === productId);
    if (product) {
        product[field] = value;
        updateEstimates();
    }
}

function renderProducts() {
    if (!elements.productsContainer) return;

    if (state.products.length === 0) {
        elements.productsContainer.classList.add('hidden');
        if (elements.emptyState) elements.emptyState.classList.remove('hidden');
        return;
    }

    elements.productsContainer.classList.remove('hidden');
    if (elements.emptyState) elements.emptyState.classList.add('hidden');

    elements.productsContainer.innerHTML = state.products.map((product, index) => `
        <div class="product-item" data-product-id="${product.id}">
            <div class="product-header">
                <div class="product-badge">
                    <span class="product-number">${index + 1}</span>
                    <span class="product-label">Product</span>
                </div>
                ${state.products.length > 1 ? `
                    <button class="remove-btn" data-remove-id="${product.id}" title="Remove product">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                ` : ''}
            </div>

            <div class="url-fetch-bar">
                <div class="url-input-wrapper">
                    <svg class="url-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                    </svg>
                    <input
                        type="url"
                        class="url-input"
                        placeholder="Paste a product URL and we'll grab the details..."
                        data-url-product-id="${product.id}"
                    >
                </div>
                <button class="btn btn-accent btn-sm url-fetch-btn" data-fetch-id="${product.id}" type="button">
                    <span class="fetch-btn-content">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.66 0 3-4.03 3-9s-1.34-9-3-9m0 18c-1.66 0-3-4.03-3-9s1.34-9 3-9"></path>
                        </svg>
                        Fetch
                    </span>
                    <span class="fetch-btn-loading" style="display: none;">
                        <span class="spinner-sm"></span>
                        Fetching...
                    </span>
                </button>
            </div>

            <div class="divider-or"><span>or enter manually</span></div>

            <div class="product-fields">
                <div class="field-row">
                    <div class="field-group" style="flex: 1;">
                        <label class="field-label">Product Name</label>
                        <input
                            type="text"
                            class="field-input"
                            placeholder="e.g., Anti-Aging Serum, Wireless Earbuds"
                            value="${escapeHtml(product.name)}"
                            data-field="name"
                            data-product-id="${product.id}"
                        >
                    </div>
                    <label class="checkbox-wrapper">
                        <input
                            type="checkbox"
                            ${product.includeProduct ? 'checked' : ''}
                            data-field="includeProduct"
                            data-product-id="${product.id}"
                        >
                        <span class="checkbox-label">Show in image</span>
                    </label>
                </div>

                <div class="field-group">
                    <label class="field-label">Product Description</label>
                    <textarea
                        class="field-textarea"
                        placeholder="Describe your product, its benefits, target audience, and key selling points. The more detail you provide, the better the ads will be!"
                        data-field="description"
                        data-product-id="${product.id}"
                    >${escapeHtml(product.description)}</textarea>
                </div>

                <div class="field-group">
                    <label class="field-label">Creative Guidance (Optional)</label>
                    <textarea
                        class="field-textarea"
                        placeholder="Any specific direction? e.g., 'Focus on anti-aging benefits', 'Lifestyle shots with young professionals', 'Emphasize the premium quality'"
                        data-field="guidance"
                        data-product-id="${product.id}"
                        style="min-height: 80px;"
                    >${escapeHtml(product.guidance)}</textarea>
                </div>
            </div>
        </div>
    `).join('');

    // Add event listeners to new elements
    attachProductListeners();

    // Update add button state
    updateAddButtonState();
}

function attachProductListeners() {
    // Remove buttons
    document.querySelectorAll('.remove-btn[data-remove-id]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const id = parseInt(btn.dataset.removeId);
            removeProduct(id);
        });
    });

    // URL fetch buttons
    document.querySelectorAll('.url-fetch-btn[data-fetch-id]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const id = parseInt(btn.dataset.fetchId);
            fetchProductFromUrl(id);
        });
    });

    // URL input - allow Enter key to trigger fetch
    document.querySelectorAll('.url-input[data-url-product-id]').forEach(input => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const id = parseInt(input.dataset.urlProductId);
                fetchProductFromUrl(id);
            }
        });
    });

    // Input fields
    document.querySelectorAll('.field-input[data-product-id], .field-textarea[data-product-id]').forEach(input => {
        input.addEventListener('input', (e) => {
            const id = parseInt(input.dataset.productId);
            const field = input.dataset.field;
            updateProduct(id, field, e.target.value);
        });
    });

    // Checkboxes
    document.querySelectorAll('input[type="checkbox"][data-product-id]').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const id = parseInt(checkbox.dataset.productId);
            const field = checkbox.dataset.field;
            updateProduct(id, field, e.target.checked);
        });
    });
}

async function fetchProductFromUrl(productId) {
    const urlInput = document.querySelector(`.url-input[data-url-product-id="${productId}"]`);
    const fetchBtn = document.querySelector(`.url-fetch-btn[data-fetch-id="${productId}"]`);

    if (!urlInput || !urlInput.value.trim()) {
        showNotification('Please paste a product URL first', 'warning');
        return;
    }

    const url = urlInput.value.trim();

    // Basic URL validation
    try {
        new URL(url);
    } catch {
        showNotification('Please enter a valid URL (e.g., https://example.com/product)', 'error');
        return;
    }

    // Set loading state
    if (fetchBtn) {
        const content = fetchBtn.querySelector('.fetch-btn-content');
        const loading = fetchBtn.querySelector('.fetch-btn-loading');
        fetchBtn.disabled = true;
        if (content) content.style.display = 'none';
        if (loading) loading.style.display = 'flex';
    }

    try {
        const formData = new FormData();
        formData.append('url', url);

        const response = await fetch('/api/scrape-product', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to fetch product info');
        }

        const data = await response.json();

        if (data.success) {
            // Update state
            updateProduct(productId, 'name', data.name);
            updateProduct(productId, 'description', data.description);

            // Re-render to show the filled data
            renderProducts();

            // Flash the product card to show it was updated
            setTimeout(() => {
                const card = document.querySelector(`[data-product-id="${productId}"]`);
                if (card) {
                    card.classList.add('url-fetched');
                    setTimeout(() => card.classList.remove('url-fetched'), 2000);
                }
            }, 100);

            showNotification(`Product info fetched for "${data.name}"`, 'success');
        }

    } catch (error) {
        console.error('Error fetching product:', error);
        showNotification('Failed to fetch product: ' + error.message, 'error');
    } finally {
        // Reset button state (may be re-rendered, so query again)
        const btn = document.querySelector(`.url-fetch-btn[data-fetch-id="${productId}"]`);
        if (btn) {
            const content = btn.querySelector('.fetch-btn-content');
            const loading = btn.querySelector('.fetch-btn-loading');
            btn.disabled = false;
            if (content) content.style.display = 'flex';
            if (loading) loading.style.display = 'none';
        }
    }
}

function updateAddButtonState() {
    if (!elements.addProductBtn) return;

    if (state.products.length >= 7) {
        elements.addProductBtn.disabled = true;
        elements.addProductBtn.innerHTML = 'Max 7 Products';
    } else {
        elements.addProductBtn.disabled = false;
        elements.addProductBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Add Product
        `;
    }
}

function updateEstimates() {
    const validProducts = state.products.filter(p => p.name.trim() || p.description.trim()).length;
    const headlines = parseInt(elements.headlinesCount?.value || 2);
    const images = parseInt(elements.imagesCount?.value || 2);

    const totalAds = validProducts * headlines * images;
    const estimatedCost = (totalAds * 0.027).toFixed(2);

    if (elements.productCount) elements.productCount.textContent = validProducts;
    if (elements.adEstimate) elements.adEstimate.textContent = totalAds;
    if (elements.outputEstimate) elements.outputEstimate.textContent = `${totalAds} ads`;
    if (elements.costEstimate) elements.costEstimate.textContent = estimatedCost;
}

// ============ Generation ============
async function startGeneration() {
    // Validate products
    const validProducts = state.products.filter(p => p.name.trim() && p.description.trim());

    if (validProducts.length === 0) {
        showNotification('Please add at least one product with a name and description', 'error');
        return;
    }

    // Get settings
    const adSize = elements.adSize?.value || 'instagram_feed';
    const headlinesCount = parseInt(elements.headlinesCount?.value || 2);
    const imagesCount = parseInt(elements.imagesCount?.value || 2);

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
    showSection('progress');
    setButtonLoading(elements.generateBtn, true);

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
        state.currentJobId = job.job_id;

        // Start polling for status
        state.pollInterval = setInterval(pollJobStatus, 2000);

    } catch (error) {
        console.error('Error starting generation:', error);
        showNotification('Failed to start generation: ' + error.message, 'error');
        showSection('input');
        setButtonLoading(elements.generateBtn, false);
    }
}

async function pollJobStatus() {
    if (!state.currentJobId) return;

    try {
        const response = await fetch(`/api/jobs/${state.currentJobId}`);
        if (!response.ok) throw new Error('Failed to get job status');

        const job = await response.json();

        // Update progress UI
        updateProgress(job.progress, job.message);

        // Check if completed or failed
        if (job.status === 'completed') {
            clearInterval(state.pollInterval);
            showResults(job.result);
        } else if (job.status === 'failed') {
            clearInterval(state.pollInterval);
            showNotification('Generation failed: ' + job.message, 'error');
            showSection('input');
            setButtonLoading(elements.generateBtn, false);
        }

    } catch (error) {
        console.error('Error polling status:', error);
    }
}

function updateProgress(percent, message) {
    if (elements.progressPercent) {
        elements.progressPercent.textContent = `${Math.round(percent)}%`;
    }
    if (elements.progressBar) {
        elements.progressBar.style.width = `${percent}%`;
    }
    if (elements.progressMessage) {
        elements.progressMessage.textContent = message;
    }

    // Update progress ring
    const progressRing = document.getElementById('progress-ring');
    if (progressRing) {
        const circumference = 2 * Math.PI * 45;
        const offset = circumference - (percent / 100) * circumference;
        progressRing.style.strokeDashoffset = offset;
    }

    // Update step indicators
    updateProgressSteps(percent);
}

function updateProgressSteps(percent) {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        const threshold = (index + 1) * 25;
        if (percent >= threshold) {
            step.classList.add('completed');
            step.classList.remove('active');
        } else if (percent >= threshold - 25) {
            step.classList.add('active');
            step.classList.remove('completed');
        } else {
            step.classList.remove('active', 'completed');
        }
    });
}

// ============ Results ============
function showResults(result) {
    showSection('results');
    setButtonLoading(elements.generateBtn, false);

    if (!result || !result.products) {
        if (elements.resultsGrid) {
            elements.resultsGrid.innerHTML = '<p class="empty-state">No results found</p>';
        }
        return;
    }

    const totalAds = result.products.reduce((sum, p) => sum + (p.final_ads?.length || 0), 0);
    if (elements.resultsCount) {
        elements.resultsCount.textContent = `Generated ${totalAds} ad variations`;
    }

    if (elements.resultsGrid) {
        elements.resultsGrid.innerHTML = result.products.map(product => {
            if (product.error) {
                return `
                    <div class="result-product">
                        <div class="result-product-header">
                            <h3 class="result-product-title">
                                <span>❌</span>
                                ${escapeHtml(product.product_name)}
                            </h3>
                            <p class="result-product-meta">Error: ${escapeHtml(product.error)}</p>
                        </div>
                    </div>
                `;
            }

            const headlines = product.headlines || [];
            const ads = product.final_ads || [];

            return `
                <div class="result-product">
                    <div class="result-product-header">
                        <h3 class="result-product-title">
                            <span>📦</span>
                            ${escapeHtml(product.product_name)}
                        </h3>
                        <p class="result-product-meta">${ads.length} ads generated</p>
                    </div>

                    <div class="result-headlines">
                        <p class="headlines-label">Headlines</p>
                        ${headlines.map(h => `
                            <p class="headline-item">"${escapeHtml(h.text)}"</p>
                        `).join('')}
                    </div>

                    <div class="result-ads-grid">
                        ${ads.map((adPath, i) => {
                const filename = adPath.split('/').pop();
                return `
                                <div class="result-ad" data-url="/api/output/${filename}">
                                    <img src="/api/output/${filename}" alt="Ad ${i + 1}" loading="lazy">
                                    <div class="result-ad-overlay">
                                        <button data-download="/api/output/${filename}" data-filename="${filename}">
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

        // Attach result listeners
        attachResultListeners();
    }
}

function attachResultListeners() {
    // Ad click to open
    document.querySelectorAll('.result-ad[data-url]').forEach(ad => {
        ad.addEventListener('click', (e) => {
            if (!e.target.closest('button')) {
                window.open(ad.dataset.url, '_blank');
            }
        });
    });

    // Download buttons
    document.querySelectorAll('button[data-download]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            downloadImage(btn.dataset.download, btn.dataset.filename);
        });
    });
}

// ============ Downloads ============
async function downloadAll() {
    if (!state.currentJobId) return;

    try {
        const response = await fetch(`/api/download-batch/${state.currentJobId}`);
        if (!response.ok) throw new Error('Failed to download');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ads_batch_${state.currentJobId.substring(0, 8)}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error('Error downloading:', error);
        showNotification('Failed to download: ' + error.message, 'error');
    }
}

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

// ============ UI Helpers ============
function showSection(section) {
    const sections = {
        input: elements.inputSection,
        progress: elements.progressSection,
        results: elements.resultsSection
    };

    Object.values(sections).forEach(el => {
        if (el) el.classList.add('hidden');
    });

    if (sections[section]) {
        sections[section].classList.remove('hidden');
    }

    // Also hide/show hero
    const hero = document.getElementById('hero');
    if (hero) {
        hero.style.display = section === 'input' ? 'block' : 'none';
    }
}

function setButtonLoading(btn, loading) {
    if (!btn) return;

    const content = btn.querySelector('.btn-content');
    const loadingEl = btn.querySelector('.btn-loading');

    if (loading) {
        btn.disabled = true;
        if (content) content.style.display = 'none';
        if (loadingEl) loadingEl.style.display = 'flex';
    } else {
        btn.disabled = false;
        if (content) content.style.display = 'flex';
        if (loadingEl) loadingEl.style.display = 'none';
    }
}

function startOver() {
    state.currentJobId = null;
    state.products = [];
    addProduct();
    showSection('input');
    updateEstimates();
}

function showNotification(message, type = 'info') {
    // Simple alert for now - could be replaced with a toast system
    alert(message);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Make functions available globally for any remaining inline handlers
window.addProduct = addProduct;
window.removeProduct = removeProduct;
window.updateProduct = updateProduct;
window.startGeneration = startGeneration;
window.downloadAll = downloadAll;
window.startOver = startOver;
