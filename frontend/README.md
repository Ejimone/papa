# Frontend Application

This is the frontend application for the project, built with React Native and Expo.

## Getting Started

Follow these steps to set up and run the application on your local machine.

### Prerequisites

Make sure you have the following installed:

*   Node.js (LTS version recommended)
*   npm (comes with Node.js)
*   Expo CLI (`npm install -g expo-cli`)

### Installation

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```

2.  Install the project dependencies:
    ```bash
    npm install
    ```

### Running the Application

To run the application, use one of the following commands:

*   **For Android emulator/device:**
    ```bash
    npm run android
    ```

*   **For iOS simulator/device:**
    ```bash
    npm run ios
    ```

*   **For web browser (development only):**
    ```bash
    npm run web
    ```

After running one of the above commands, Expo will open a new tab in your browser with the Expo Dev Tools. You can scan the QR code with your mobile device using the Expo Go app (available on App Store and Google Play) to open the application on your phone.

## Project Structure

*   `src/api`: API client for interacting with the backend.
*   `src/components`: Reusable UI components.
*   `src/navigation`: Navigation setup (Stack and Tab navigators).
*   `src/screens`: Individual application screens.
*   `src/store`: Redux store for state management.
*   `src/theme`: Theming and styling configurations.
*   `src/utils`: Utility functions.
