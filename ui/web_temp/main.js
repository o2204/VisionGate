document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    lucide.createIcons();

    // --- State & Mock Data ---
    let currentTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeUI();

    const mockUsers = [
        { name: 'Alex Johnson', email: 'alex@visiongate.io', role: 'Admin', status: 'Active', avatar: 'https://i.pravatar.cc/150?u=1' },
        { name: 'Sarah Miller', email: 'sarah@visiongate.io', role: 'User', status: 'Active', avatar: 'https://i.pravatar.cc/150?u=2' },
        { name: 'David Chen', email: 'david@visiongate.io', role: 'User', status: 'Inactive', avatar: 'https://i.pravatar.cc/150?u=3' },
        { name: 'Elena Rodriguez', email: 'elena@visiongate.io', role: 'Admin', status: 'Active', avatar: 'https://i.pravatar.cc/150?u=4' }
    ];

    const mockLogs = [
        { id: 'AC-9021', user: 'Alex Johnson', role: 'Admin', time: '10:45 AM', confidence: '98.4%', status: 'Granted' },
        { id: 'AC-9020', user: 'Sarah Miller', role: 'User', time: '10:32 AM', confidence: '95.1%', status: 'Granted' },
        { id: 'AC-9019', user: 'Unknown', role: 'N/A', time: '10:15 AM', confidence: '12.4%', status: 'Denied' },
        { id: 'AC-9018', user: 'David Chen', role: 'User', time: '09:58 AM', confidence: '97.8%', status: 'Granted' },
        { id: 'AC-9017', user: 'Elena Rodriguez', role: 'Admin', time: '09:42 AM', confidence: '99.2%', status: 'Granted' },
        { id: 'AC-9016', user: 'Unknown', role: 'N/A', time: '09:10 AM', confidence: '4.2%', status: 'Denied' }
    ];

    // --- DOM Elements ---
    const navItems = document.querySelectorAll('.nav-item[data-section]');
    const sections = document.querySelectorAll('.section');
    const sectionTitle = document.getElementById('current-section-title');
    const themeToggle = document.getElementById('theme-toggle');
    
    // Table bodies
    const recentActivityBody = document.getElementById('recent-activity-body');
    const allLogsBody = document.getElementById('all-logs-body');
    const userManagementBody = document.getElementById('user-management-body');

    // Scan Modal & Video Elements
    const scanModal = document.getElementById('scan-modal');
    const startScanBtn = document.getElementById('start-scan-btn');
    const cancelScanBtn = document.getElementById('cancel-scan-btn');
    const triggerScanBtn = document.getElementById('trigger-scan-logic');
    const closeScanBtn = document.getElementById('close-scan-btn');
    const scanResult = document.getElementById('scan-result');
    const scanMetadata = document.getElementById('scan-metadata');
    const scanLine = document.getElementById('scan-line');
    
    const video = document.getElementById('video');
    const canvas = document.getElementById('overlay');

    let modelsLoaded = false;
    let recognitionInterval;

    // --- Face API Integration ---
    async function loadModels() {
        if (modelsLoaded) return;
        
        scanMetadata.innerHTML = `[SYS]: LOADING AI MODELS...`;
        
        try {
            // Using a reliable CDN for models
            const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/';
            
            await Promise.all([
                faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
                faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
                faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
                faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL)
            ]);
            
            modelsLoaded = true;
            scanMetadata.innerHTML = `[SYS]: MODELS LOADED READY.`;
        } catch (err) {
            console.error("Model loading failed:", err);
            scanMetadata.innerHTML = `<span style="color:var(--danger)">[ERR]: MODEL LOAD FAILED</span>`;
        }
    }

    async function startWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: {} });
            video.srcObject = stream;
            
            // Wait for video to be ready
            return new Promise((resolve) => {
                video.onloadedmetadata = () => {
                    resolve();
                };
            });
        } catch (err) {
            console.error("Webcam access denied:", err);
            scanMetadata.innerHTML = `<span style="color:var(--danger)">[ERR]: CAMERA DENIED</span>`;
        }
    }

    function stopWebcam() {
        if (video.srcObject) {
            const tracks = video.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            video.srcObject = null;
        }
        if (recognitionInterval) clearInterval(recognitionInterval);
    }

    async function startFaceDetection() {
        const displaySize = { width: video.offsetWidth, height: video.offsetHeight };
        faceapi.matchDimensions(canvas, displaySize);

        recognitionInterval = setInterval(async () => {
            if (!modelsLoaded) return;

            const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks()
                .withFaceExpressions();

            const resizedDetections = faceapi.resizeResults(detections, displaySize);
            
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Custom drawing to keep it aesthetic
            resizedDetections.forEach(detection => {
                const box = detection.detection.box;
                ctx.strokeStyle = 'hsl(221, 83%, 53%)';
                ctx.lineWidth = 2;
                ctx.strokeRect(box.x, box.y, box.width, box.height);
                
                // Show confidence
                const score = (detection.detection.score * 100).toFixed(1);
                scanMetadata.innerHTML = `
                    [SYS]: SCAN ACTIVE<br>
                    [FACE]: DETECTED<br>
                    [CONFIDENCE]: ${score}%<br>
                    [EXPRESSION]: ${Object.entries(detection.expressions).reduce((a, b) => a[1] > b[1] ? a : b)[0]}
                `;
            });

            if (detections.length === 0) {
                scanMetadata.innerHTML = `[SYS]: SEARCHING FOR FACE...`;
            }
        }, 100);
    }

    // --- Navigation Logic ---
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSection = item.getAttribute('data-section');
            if (!targetSection) return;

            // Update Active Nav
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Show Section
            sections.forEach(section => {
                section.classList.remove('active');
                if (section.id === `${targetSection}-section`) {
                    section.classList.add('active');
                }
            });

            // Update Title
            sectionTitle.textContent = item.querySelector('span').textContent;
        });
    });

    // --- Theme Logic ---
    themeToggle.addEventListener('click', () => {
        currentTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);
        localStorage.setItem('theme', currentTheme);
        updateThemeUI();
    });

    function updateThemeUI() {
        const sunIcon = document.getElementById('theme-icon-sun');
        const moonIcon = document.getElementById('theme-icon-moon');
        if (currentTheme === 'light') {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        } else {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        }
    }

    // --- Data Rendering ---
    function renderTables() {
        recentActivityBody.innerHTML = mockLogs.slice(0, 4).map(log => `
            <tr>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--primary-light); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; color: var(--primary);">
                            ${log.user[0]}
                        </div>
                        ${log.user}
                    </div>
                </td>
                <td>${log.role}</td>
                <td>${log.time}</td>
                <td><span class="status-badge ${log.status === 'Granted' ? 'status-granted' : 'status-denied'}">${log.status}</span></td>
            </tr>
        `).join('');

        allLogsBody.innerHTML = mockLogs.map(log => `
            <tr>
                <td>#${log.id}</td>
                <td>${log.user}</td>
                <td>${log.role}</td>
                <td>${log.time}</td>
                <td>${log.confidence}</td>
                <td><span class="status-badge ${log.status === 'Granted' ? 'status-granted' : 'status-denied'}">${log.status}</span></td>
            </tr>
        `).join('');

        userManagementBody.innerHTML = mockUsers.map(user => `
            <tr>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <img src="${user.avatar}" alt="${user.name}" style="width: 36px; height: 36px; border-radius: 50%;">
                        <span style="font-weight: 600;">${user.name}</span>
                    </div>
                </td>
                <td>${user.email}</td>
                <td>${user.role}</td>
                <td><span style="display: flex; align-items: center; gap: 0.5rem;"><div style="width: 8px; height: 8px; border-radius: 50%; background: ${user.status === 'Active' ? 'var(--success)' : 'var(--text-muted)'};"></div> ${user.status}</span></td>
                <td>
                    <button class="btn btn-ghost" style="padding: 0.25rem;"><i data-lucide="edit-2" style="width: 16px;"></i></button>
                    <button class="btn btn-ghost" style="padding: 0.25rem; color: var(--danger);"><i data-lucide="trash-2" style="width: 16px;"></i></button>
                </td>
            </tr>
        `).join('');
        
        lucide.createIcons();
    }

    renderTables();

    // --- Face Scan Sequence Logic ---
    startScanBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        scanModal.classList.add('active');
        resetScan();
        await loadModels();
        await startWebcam();
        startFaceDetection();
    });

    cancelScanBtn.addEventListener('click', () => {
        scanModal.classList.remove('active');
        stopWebcam();
    });

    closeScanBtn.addEventListener('click', () => {
        scanModal.classList.remove('active');
        stopWebcam();
    });

    triggerScanBtn.addEventListener('click', () => {
        startVerificationSequence();
    });

    function resetScan() {
        scanResult.classList.remove('active');
        scanLine.style.animationPlayState = 'paused';
        scanMetadata.innerHTML = `[SYS]: INITIALIZING CAMERA...`;
        triggerScanBtn.style.display = 'flex';
        cancelScanBtn.style.display = 'flex';
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    async function startVerificationSequence() {
        triggerScanBtn.style.display = 'none';
        cancelScanBtn.style.display = 'none';
        scanLine.style.animationPlayState = 'running';
        
        // Wait 3 seconds for "analysis"
        setTimeout(async () => {
            const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions());
            
            if (detections.length > 0) {
                showScanResult(true, (detections[0].score * 100).toFixed(1));
            } else {
                showScanResult(false, 0);
            }
        }, 3000);
    }

    function showScanResult(isSuccess, score) {
        scanLine.style.animationPlayState = 'paused';
        const resultIcon = document.getElementById('result-icon');
        const resultTitle = document.getElementById('result-title');
        const resultMsg = document.getElementById('result-msg');

        if (isSuccess) {
            resultIcon.innerHTML = `<i data-lucide="check-circle" style="color: var(--success); width: 48px; height: 48px;"></i>`;
            resultTitle.textContent = "Access Granted";
            resultTitle.style.color = "var(--success)";
            resultMsg.textContent = `Identity Verified: ${score}% Confidence`;
            
            // Add to logs
            const newLog = {
                id: 'AC-' + Math.floor(9000 + Math.random() * 1000),
                user: 'Mariam (Admin)',
                role: 'Admin',
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                confidence: score + '%',
                status: 'Granted'
            };
            mockLogs.unshift(newLog);
            renderTables();
        } else {
            resultIcon.innerHTML = `<i data-lucide="x-circle" style="color: var(--danger); width: 48px; height: 48px;"></i>`;
            resultTitle.textContent = "Access Denied";
            resultTitle.style.color = "var(--danger)";
            resultMsg.textContent = "No Face Detected or Match Too Low";
        }

        lucide.createIcons();
        scanResult.classList.add('active');
        if (recognitionInterval) clearInterval(recognitionInterval);
    }
});
