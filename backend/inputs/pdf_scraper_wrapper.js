/** 
 * @typedef {import('../../frontend/node_modules/botasaurus-controls/dist/index').Controls} Controls 
 */ 

/**
 * @param {Controls} controls 
 */
function getInput(controls) {
    controls
      // Render a text input that accepts a single link or multiple links separated by commas
      .listOfLinks('links', {
        isRequired: true,
        placeholder: "Enter the link you want to scrape",
        defaultValue: [
          "https://oceanofpdf.com/category/languages/afrikaans-language-books/",
          "https://oceanofpdf.com/category/languages/albanian-language-books/"
      ]
      })
  }
  
