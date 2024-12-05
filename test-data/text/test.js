// 直接从CDN导入axios
import axios from "https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js";

class HelloWorld {
  constructor() {
    this.messageElement = document.getElementById("hello-message");
  }

  async fetchAndDisplayMessage() {
    try {
      const response = await axios.get(
        "https://jsonplaceholder.typicode.com/posts/1"
      );
      // Assuming we want to use the title of the post as our "Hello, World!" message
      this.messageElement.textContent = response.data.title || "Hello, World!";
    } catch (error) {
      console.error(`There was an error fetching the URL: ${error.message}`);
      this.messageElement.textContent =
        "An error occurred while fetching the message.";
    }
  }
}
