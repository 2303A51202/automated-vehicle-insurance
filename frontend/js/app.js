document.addEventListener('DOMContentLoaded', () => {
    const claimForm = document.getElementById('claim-form');
    const imageInput = document.getElementById('image-input');
    const fileList = document.getElementById('file-list');
    const claimedBrandSelect = document.getElementById('claimed_brand');
    const claimedModelSelect = document.getElementById('claimed_model');
    
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');
    const resultsPanel = document.getElementById('results-panel');
    const pipelineStatus = document.getElementById('pipeline-status');
    const progressBarFill = document.getElementById('progress-bar-fill');

    // Dynamic Cascading Model Mapping per Brand (Synced strictly with repair_costs.json)
    const vehicleModelsMap = {
        "Hyundai": ["Creta", "i20", "Verna", "Venue"],
        "Toyota": ["Fortuner", "Innova Crysta", "Glanza"],
        "Tata": ["Nexon", "Harrier", "Safari", "Punch"],
        "Kia": ["Seltos", "Sonet"],
        "Honda": ["City", "Amaze", "Elevate"],
        "BMW": ["3 Series", "X3"],
        "Mercedes": ["C-Class", "GLC"]
    };

    function updateModelOptions(selectedBrand) {
        claimedModelSelect.innerHTML = '';
        const models = vehicleModelsMap[selectedBrand] || ["Standard"];
        models.forEach(model => {
            const opt = document.createElement('option');
            opt.value = model;
            opt.textContent = model;
            claimedModelSelect.appendChild(opt);
        });
    }

    // Initialize models for default selected brand
    if (claimedBrandSelect) {
        updateModelOptions(claimedBrandSelect.value);
        claimedBrandSelect.addEventListener('change', (e) => {
            updateModelOptions(e.target.value);
        });
    }

    let uploadedFiles = [];

    // File Dropzone Handling
    imageInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        for (let file of files) {
            if (!uploadedFiles.some(f => f.name === file.name)) {
                uploadedFiles.push(file);
            }
        }
        renderFileChips();
    }

    function renderFileChips() {
        fileList.innerHTML = '';
        uploadedFiles.forEach((file, idx) => {
            const chip = document.createElement('div');
            chip.className = 'file-preview-chip';
            chip.innerHTML = `
                <i class="fa-solid fa-file-image"></i>
                <span>${file.name}</span>
                <i class="fa-solid fa-xmark remove-btn" onclick="removeFile(${idx})"></i>
            `;
            fileList.appendChild(chip);
        });
    }

    window.removeFile = function(index) {
        uploadedFiles.splice(index, 1);
        renderFileChips();
    };

    // Form Submission to AI Pipeline Endpoint
    claimForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const brand = document.getElementById('claimed_brand').value;
        const model = document.getElementById('claimed_model').value;
        const description = document.getElementById('claim_description').value;

        if (uploadedFiles.length < 3) {
            alert('⚠️ Please upload at least 3 vehicle photos:\n1. Front View (for Logo Detection)\n2. Rear View (for Badge OCR & Model Determination)\n3. Damage View (for Assessment)');
            return;
        }

        const formData = new FormData();
        formData.append('claimed_brand', brand);
        formData.append('claimed_model', model);
        formData.append('claim_description', description);
        
        uploadedFiles.forEach(file => {
            formData.append('images', file);
        });

        // UI State Transitions
        emptyState.classList.add('hidden');
        resultsPanel.classList.add('hidden');
        loadingState.classList.remove('hidden');

        // Animate Pipeline Steps
        const stages = [
            "Evaluating OpenCV image blur, resolution, and lighting...",
            "Running YOLO logo detection & EfficientNet classification...",
            "Reading rear badge text with EasyOCR...",
            "Computing pHash & CLIP embeddings for duplicate check...",
            "Merging multi-view detections with Multi-Image Fusion...",
            "Running SegFormer segmentation for damage area ratios...",
            "Evaluating severity rules & repair vs replace matrix...",
            "Querying part repair & labor cost database...",
            "Analyzing claim description with DistilBERT NLP...",
            "Calculating explainable multi-factor fraud score...",
            "Generating official assessment PDF report..."
        ];

        let step = 0;
        const interval = setInterval(() => {
            if (step < stages.length) {
                pipelineStatus.textContent = stages[step];
                const pct = Math.round(((step + 1) / stages.length) * 100);
                progressBarFill.style.width = `${pct}%`;
                step++;
            }
        }, 300);

        try {
            const response = await fetch('/api/claims/assess', {
                method: 'POST',
                body: formData
            });

            clearInterval(interval);

            if (!response.ok) {
                const err = await response.json();
                alert(`Error running claim pipeline: ${err.detail || 'Unknown error'}`);
                loadingState.classList.add('hidden');
                emptyState.classList.remove('hidden');
                return;
            }

            const data = await response.json();
            
            loadingState.classList.add('hidden');
            resultsPanel.classList.remove('hidden');
            
            renderResults(data);

        } catch (error) {
            clearInterval(interval);
            alert(`Network error connecting to API: ${error.message}`);
            loadingState.classList.add('hidden');
            emptyState.classList.remove('hidden');
        }
    });

    // Render Pipeline Results
    function renderResults(data) {
        document.getElementById('res-claim-id').textContent = data.claim_id;
        
        // Vehicle verification badge
        const vehVer = data.vehicle_verification;
        const vehVerElem = document.getElementById('res-veh-ver');
        if (vehVer.is_verified) {
            vehVerElem.textContent = `MATCHED (${vehVer.confidences.overall * 100}%)`;
            vehVerElem.className = 'stat-value badge-success';
        } else {
            vehVerElem.textContent = `MISMATCH`;
            vehVerElem.className = 'stat-value badge-high-risk';
        }

        // Cost Total
        document.getElementById('res-grand-total').textContent = `₹${data.cost_estimate.grand_total.toLocaleString()}`;

        // Fraud Score
        const fraud = data.fraud_assessment;
        const fraudElem = document.getElementById('res-fraud-score');
        fraudElem.textContent = `${fraud.fraud_score} / 100 (${fraud.risk_tier.toUpperCase()})`;
        if (fraud.fraud_score >= 60) {
            fraudElem.className = 'stat-value badge-high-risk';
        } else {
            fraudElem.className = 'stat-value badge-low-risk';
        }

        // Tab 1: Verification Details
        const vehGrid = document.getElementById('veh-details-grid');
        vehGrid.innerHTML = `
            <div class="info-item"><label>Claimed Vehicle</label><span>${vehVer.claimed.brand} ${vehVer.claimed.model}</span></div>
            <div class="info-item"><label>Detected Vehicle</label><span>${vehVer.detected.brand} ${vehVer.detected.model}</span></div>
            <div class="info-item"><label>Badge OCR Text</label><span>${vehVer.detected.badge_ocr}</span></div>
            <div class="info-item"><label>Logo Confidence</label><span>${vehVer.confidences.logo * 100}%</span></div>
            <div class="info-item"><label>Classifier Confidence</label><span>${vehVer.confidences.model_classification * 100}%</span></div>
            <div class="info-item"><label>Overall Verified</label><span>${vehVer.is_verified ? 'YES' : 'NO'}</span></div>
        `;

        const qualityList = document.getElementById('quality-list');
        qualityList.innerHTML = '';
        data.quality_assessments.forEach((q, idx) => {
            const div = document.createElement('div');
            div.className = 'reason-chip';
            div.innerHTML = `<strong>Image #${idx+1}:</strong> Quality Score: ${q.score*100}% | Blur Score: ${q.blur_score} | Res: ${q.resolution} — ${q.reasons[0]}`;
            qualityList.appendChild(div);
        });

        // Tab 2: Damage & Fusion Table
        const dmgBody = document.getElementById('damage-table-body');
        dmgBody.innerHTML = '';
        data.fused_inventory.forEach((item, idx) => {
            const seg = data.segmentation_results[idx] || {};
            const sev = data.severity_assessments[idx] || {};
            const dec = data.repair_decisions[idx] || {};

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${item.part}</strong></td>
                <td><span class="badge">${item.damage_type}</span></td>
                <td>${seg.damage_percentage || 10}%</td>
                <td><span class="badge ${sev.severity_level === 'Severe' ? 'badge-high-risk' : 'badge-low-risk'}">${sev.severity_level || 'Minor'}</span></td>
                <td><strong>${dec.decision || 'Repair'}</strong></td>
                <td>${Math.round(item.max_confidence * 100)}%</td>
            `;
            dmgBody.appendChild(tr);
        });

        // Tab 3: Cost Table
        const costBody = document.getElementById('cost-table-body');
        costBody.innerHTML = '';
        data.cost_estimate.line_items.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.part}</td>
                <td>${item.work_type}</td>
                <td>₹${item.part_cost.toLocaleString()}</td>
                <td>₹${item.labor_cost.toLocaleString()}</td>
                <td><strong>₹${item.subtotal.toLocaleString()}</strong></td>
            `;
            costBody.appendChild(tr);
        });
        document.getElementById('cost-grand-total-cell').textContent = `₹${data.cost_estimate.grand_total.toLocaleString()}`;

        // Tab 4: Fraud Banner & Reasons
        const fraudBanner = document.getElementById('fraud-banner');
        const fraudCircle = document.getElementById('fraud-circle');
        fraudCircle.textContent = fraud.fraud_score;
        document.getElementById('fraud-tier-title').textContent = fraud.risk_tier;
        document.getElementById('fraud-recommendation').textContent = fraud.recommendation;

        const reasonsList = document.getElementById('fraud-reasons-list');
        reasonsList.innerHTML = '';
        fraud.explanation_reasons.forEach(r => {
            const chip = document.createElement('div');
            chip.className = 'reason-chip';
            chip.textContent = r;
            reasonsList.appendChild(chip);
        });

        // PDF Link
        document.getElementById('download-pdf-btn').href = data.pdf_report_url;
    }

    // Global Tab Switching
    window.switchTab = function(tabId) {
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));

        document.querySelector(`[onclick="switchTab('${tabId}')"]`).classList.add('active');
        document.getElementById(tabId).classList.remove('hidden');
    };
});
