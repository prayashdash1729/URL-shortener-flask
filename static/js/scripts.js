function copyToClipboard(text) {
  // Create a temporary textarea element
  const textarea = document.createElement('textarea');
  textarea.value = text;

  // Set the position and visibility to keep it hidden
  textarea.style.position = 'fixed';
  textarea.style.top = '-9999px';

  // Append the textarea to the document
  document.body.appendChild(textarea);

  // Select the text inside the textarea
  textarea.select();

  // Copy the selected text to the clipboard
  document.execCommand('copy');

  // Remove the textarea from the document
  document.body.removeChild(textarea);

  // Show a notification
  alert('Copied to clipboard: ' + text);
}
