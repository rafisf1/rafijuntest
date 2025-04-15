const fs = require('fs');
const path = require('path');

// Function to convert image to base64
function imageToBase64(imagePath) {
    const image = fs.readFileSync(imagePath);
    return `data:image/jpeg;base64,${image.toString('base64')}`;
}

// Read the original HTML file
const htmlContent = fs.readFileSync('index.html', 'utf8');

// Get all image paths
const imagePaths = [
    'images anvi test2/image1.JPG',
    'images anvi test2/image2.JPG',
    'images anvi test2/image3.JPG',
    'images anvi test2/image4.JPG',
    'images anvi test2/image5.JPG',
    'images anvi test2/image6.JPG',
    'images anvi test2/image7.JPG',
    'images anvi test2/image8.JPG',
    'images anvi test2/image9.JPG',
    'images anvi test2/image10.jpg',
    'images anvi test2/image11.JPG',
    'images anvi test2/image12.JPEG'
];

// Convert images to base64 and create the images array
const imagesArray = imagePaths.map((path, index) => {
    const base64 = imageToBase64(path);
    return `{ id: ${index + 1}, url: '${base64}', rating: 1200 }`;
});

// Replace the image loading code with the pre-converted images
const newHtmlContent = htmlContent.replace(
    /let IMAGES = \[\];\s*async function initializeImages\(\) {[\s\S]*?initializeImages\(\);}/,
    `let IMAGES = [\n    ${imagesArray.join(',\n    ')}\n];\n\nfunction init() {\n    console.log('Starting application...');\n    loadState();\n    generateComparisons();\n    showNextComparison();\n    setupKeyboardControls();\n}`
);

// Write the new HTML file
fs.writeFileSync('index_standalone.html', newHtmlContent);

console.log('Standalone version created successfully!'); 