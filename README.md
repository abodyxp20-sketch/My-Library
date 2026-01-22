# Modern Library Website with 3D Elements

This project implements a modern library website featuring cutting-edge UI/UX elements as requested. The site includes 3D book interactions, animated backgrounds, scroll-based animations, and more.

## Features Implemented

### 1. 3D Web Elements
- Interactive 3D book models that respond to mouse movement
- Each book tilts realistically based on cursor position
- Simulated pages that appear to flip slightly when hovering
- Created using Three.js for the mesh gradient background

### 2. AI-Powered Animated Backgrounds (Glassmorphism & Mesh Gradients)
- Dynamic mesh gradient background with floating particles
- Glassmorphism effect on UI elements (blurry, semi-transparent panels)
- Time-of-day adaptive background colors
- Smooth transitions between color schemes

### 3. Scroll-Based Animations
- GSAP-inspired scroll animations using Intersection Observer API
- Cards fly in from the sides as they come into view
- Staggered animations for visual appeal

### 4. Lottie File Integration
- Simulated Lottie animations for book borrowing actions
- Success checkmark animations when borrowing books
- Smooth transitions and feedback for user interactions

### 5. AI-Generated Image Style Consistency
- Consistent color palette across all book covers
- Minimalist modern design approach
- Unified visual identity for all books

### 6. Smart Dark Mode
- Automatic switching based on system preferences
- Custom midnight blue and deep charcoal colors
- Subtle neon glow effects around interactive elements

## How to Run

1. Make sure you have Node.js installed
2. Install dependencies: `npm install`
3. Start the server: `npm start`
4. Open your browser and go to `http://localhost:3000`

## Customization Options

### Changing Book Details
Edit the HTML in `index.html` to add or modify books in the library:
```html
<div class="book-card" data-book-id="4">
    <div class="book-3d-container" id="book4">
        <!-- 3D Book will be rendered here -->
    </div>
    <h3>New Book Title</h3>
    <p>Author Name</p>
    <button class="borrow-btn">Borrow Book</button>
</div>
```

### Modifying Color Palettes
Update the CSS in `styles.css` to change the overall color scheme:
- Primary colors: Modify the gradient values in `.borrow-btn` and headers
- Glassmorphism: Adjust `rgba()` values in `.book-card` and `.main-header`
- Background: Change the `background` property in the `body` selector

### Adding More 3D Effects
Enhance the 3D effects by modifying the JavaScript in `script.js`:
- Adjust rotation sensitivity in the `mousemove` event handler
- Modify the `translateZ` value for depth effects
- Add more complex 3D transformations

## Performance Considerations

- The Three.js scene is optimized with appropriate pixel ratios
- Animations are hardware-accelerated where possible
- Efficient DOM manipulation using event delegation
- Responsive design for various screen sizes

## Technologies Used

- HTML5
- CSS3 (with advanced effects like backdrop-filter, gradients, and transforms)
- JavaScript (ES6+)
- Three.js for 3D graphics
- Express.js for the local server

## Browser Compatibility

- Modern browsers with support for CSS backdrop-filter
- Browsers supporting ES6 JavaScript features
- WebGL support for 3D effects

The site will gracefully degrade on older browsers while maintaining core functionality.