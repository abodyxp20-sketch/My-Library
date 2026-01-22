// Initialize Three.js scene for mesh gradient background
function initMeshGradient() {
    const canvas = document.getElementById('mesh-gradient-bg');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Create dynamic mesh gradient
    const geometry = new THREE.IcosahedronGeometry(5, 64);
    const material = new THREE.MeshBasicMaterial({
        color: 0x4361ee,
        wireframe: true
    });

    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    camera.position.z = 8;

    // Add floating particles
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 1000;
    const posArray = new Float32Array(particlesCount * 3);

    for(let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 20;
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

    const particlesMaterial = new THREE.PointsMaterial({
        size: 0.02,
        color: 0xffffff
    });

    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particlesMesh);

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        
        mesh.rotation.x += 0.001;
        mesh.rotation.y += 0.002;
        
        particlesMesh.rotation.y += 0.0005;
        
        renderer.render(scene, camera);
    }

    animate();

    // Handle resize
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// Initialize 3D book interactions
function init3DBooks() {
    const books = document.querySelectorAll('.book-3d-container');
    
    books.forEach(bookContainer => {
        // Create a simple 3D book representation using HTML/CSS for now
        // In a real implementation, we would load a Spline model here
        const bookElement = document.createElement('div');
        bookElement.className = 'book-3d-model';
        bookElement.innerHTML = `
            <div class="book-cover">
                <div class="spine"></div>
                <div class="front-cover">
                    <div class="title-placeholder"></div>
                    <div class="author-placeholder"></div>
                </div>
                <div class="pages">
                    <div class="page"></div>
                    <div class="page"></div>
                    <div class="page"></div>
                </div>
            </div>
        `;
        bookContainer.appendChild(bookElement);
        
        // Add mouse move interaction
        bookContainer.addEventListener('mousemove', (e) => {
            const rect = bookContainer.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateY = (x - centerX) / 25; // Reduced sensitivity
            const rotateX = (centerY - y) / 25; // Inverted for natural feel
            
            const bookModel = bookContainer.querySelector('.book-3d-model');
            bookModel.style.transform = `rotateY(${rotateY}deg) rotateX(${rotateX}deg) translateZ(20px)`;
        });
        
        bookContainer.addEventListener('mouseleave', () => {
            const bookModel = bookContainer.querySelector('.book-3d-model');
            bookModel.style.transform = 'rotateY(0) rotateX(0) translateZ(0)';
        });
    });
}

// Implement scroll-based animations using Intersection Observer
function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                // Add subtle animation when element comes into view
                entry.target.style.animation = 'fadeInUp 0.8s forwards';
            }
        });
    }, observerOptions);

    // Observe all book cards
    document.querySelectorAll('.book-card').forEach(card => {
        observer.observe(card);
    });
}

// Initialize Lottie animations
function initLottieAnimations() {
    // Since we don't have actual Lottie files, we'll simulate the effect with CSS animations
    
    // Borrow success animation
    const borrowButtons = document.querySelectorAll('.borrow-btn');
    borrowButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Create a temporary checkmark icon
            const checkmark = document.createElement('div');
            checkmark.className = 'temp-checkmark';
            checkmark.innerHTML = '✓';
            checkmark.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 4rem;
                color: #4ade80;
                z-index: 1000;
                animation: checkmarkAnimation 1.5s forwards;
            `;
            
            document.body.appendChild(checkmark);
            
            setTimeout(() => {
                document.body.removeChild(checkmark);
            }, 1500);
            
            // Change button text temporarily
            const originalText = this.textContent;
            this.textContent = 'Borrowed!';
            this.style.background = 'linear-gradient(45deg, #4ade80, #22c55e)';
            
            setTimeout(() => {
                this.textContent = originalText;
                this.style.background = 'linear-gradient(45deg, #4361ee, #3a0ca3)';
            }, 2000);
        });
    });
}

// Add custom animations to CSS
function addDynamicStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes checkmarkAnimation {
            0% { 
                opacity: 0; 
                transform: translate(-50%, -50%) scale(0); 
            }
            20% { 
                opacity: 1; 
                transform: translate(-50%, -50%) scale(1.2); 
            }
            50% { 
                opacity: 1; 
                transform: translate(-50%, -50%) scale(1); 
            }
            100% { 
                opacity: 0; 
                transform: translate(-50%, -50%) scale(1) translateY(-100px); 
            }
        }
        
        .book-cover {
            position: relative;
            width: 100%;
            height: 100%;
            transform-style: preserve-3d;
            transition: transform 0.5s ease;
        }
        
        .spine {
            position: absolute;
            width: 20px;
            height: 100%;
            background: linear-gradient(to right, #333, #555, #333);
            left: 10px;
            top: 0;
            border-radius: 3px 0 0 3px;
        }
        
        .front-cover {
            position: absolute;
            width: calc(100% - 20px);
            height: 100%;
            background: linear-gradient(135deg, #3a0ca3, #4361ee);
            left: 20px;
            top: 0;
            border-radius: 0 5px 5px 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.3);
        }
        
        .title-placeholder {
            width: 70%;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
            margin-bottom: 10px;
        }
        
        .author-placeholder {
            width: 50%;
            height: 15px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 3px;
        }
        
        .pages {
            position: absolute;
            width: calc(100% - 25px);
            height: 100%;
            left: 25px;
            top: 0;
        }
        
        .page {
            position: absolute;
            width: 95%;
            height: 95%;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 0 4px 4px 0;
            left: 2%;
            top: 2.5%;
            background: rgba(255, 255, 255, 0.05);
            transform-origin: left center;
        }
        
        .page:nth-child(2) {
            transform: rotateY(-2deg);
        }
        
        .page:nth-child(3) {
            transform: rotateY(-4deg);
        }
        
        .visible {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);
}

// Initialize dark mode toggle
function initDarkMode() {
    // Check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Apply dark mode if preferred
    if (prefersDark) {
        document.body.classList.add('dark-mode');
    }
    
    // Listen for changes in system preference
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        if (event.matches) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    });
}

// Initialize all features
document.addEventListener('DOMContentLoaded', () => {
    initMeshGradient();
    init3DBooks();
    initScrollAnimations();
    initLottieAnimations();
    addDynamicStyles();
    initDarkMode();
});

// Update background based on time of day
function updateBackgroundByTime() {
    const hour = new Date().getHours();
    let gradientColors;
    
    if (hour >= 6 && hour < 12) {
        // Morning - warm colors
        gradientColors = ['#ff9a9e', '#fad0c4', '#fbc2eb'];
    } else if (hour >= 12 && hour < 18) {
        // Afternoon - bright blue
        gradientColors = ['#a1c4fd', '#c2e9fb', '#4361ee'];
    } else if (hour >= 18 && hour < 22) {
        // Evening - purple/orange
        gradientColors = ['#667eea', '#764ba2', '#ffecd2'];
    } else {
        // Night - deep blues/purples
        gradientColors = ['#1a1a2e', '#16213e', '#0f3460'];
    }
    
    document.body.style.background = `linear-gradient(135deg, ${gradientColors[0]}, ${gradientColors[1]}, ${gradientColors[2]})`;
}

// Update background initially and every hour
updateBackgroundByTime();
setInterval(updateBackgroundByTime, 3600000); // Every hour