//     const data = {{ search_dict | tojson}};
//
//     const searchInput = document.getElementById('default-search');
//     const searchResultsContainer = document.getElementById('search-results');
//
//     // Event listener for input changes
//     searchInput.addEventListener('input', function () {
//         const searchTerm = searchInput.value.toLowerCase();
//         const filteredResults = Object.entries(data).filter(([uuid, note_name]) => note_name.toLowerCase().includes(searchTerm));
//         displayResults(filteredResults);
//     });
//
//     // Function to display search results
//     function displayResults(results) {
//     searchResultsContainer.innerHTML = '';
//
//     if (searchInput.value === '') {
//         return;
//     }
//
//     if (results.length === 0) {
//         searchResultsContainer.innerHTML = '<p class="text-gray-500">No results found.</p>';
//         return;
//     }
//
//     results.forEach(([uuid, note_name]) => {
//         const div = document.createElement('div');
//         div.classList.add('relative', 'p-2', 'border', 'rounded-md', 'mb-2', 'bg-white');
//
//         const title = document.createElement('p');
//         title.textContent = note_name;
//         title.classList.add('text-gray-700', 'mb-2');
//
//         // Open button
//         const openButton = document.createElement('button');
//         openButton.textContent = 'Open';
//         openButton.classList.add('text-white', 'absolute', 'right-2.5', 'bottom-2.5', 'bg-blue-700', 'hover:bg-blue-800', 'focus:ring-4', 'focus:outline-none', 'focus:ring-blue-300', 'font-medium', 'rounded-lg', 'text-sm', 'px-4', 'py-2', 'dark:bg-blue-600', 'dark:hover:bg-blue-700', 'dark:focus:ring-blue-800');
//         openButton.addEventListener('click', () => {
//             window.open('/qp-display?pdf=' + uuid, '_blank');
//         });
//
//         // Pin button
//         const pinButton = document.createElement('button');
//         pinButton.textContent = 'Pin';
//         pinButton.classList.add('text-white', 'absolute', 'right-20', 'bottom-2.5', 'bg-green-700', 'hover:bg-green-800', 'focus:ring-green-300', 'font-medium', 'rounded-lg', 'text-sm', 'px-4', 'py-2', 'dark:bg-green-600', 'dark:hover:bg-green-700');
//         pinButton.addEventListener('click', () => {
//             // Toggle the pinned state on click
//             const isPinned = div.getAttribute('data-pinned') === '1';
//             div.setAttribute('data-pinned', isPinned ? '0' : '1');
//             // Optionally, change the button text to reflect the state
//             pinButton.textContent = isPinned ? 'Pin' : 'Unpin';
//             console.log('Pinned:', uuid, !isPinned); // Log the new state
//         });
//
//
//         div.appendChild(title);
//         div.appendChild(openButton);
//         div.appendChild(pinButton); // Append the pin button next to the open button
//         searchResultsContainer.appendChild(div);
//     });
// }