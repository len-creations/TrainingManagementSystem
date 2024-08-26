document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.querySelector('#search-form');
    const searchInput = searchForm.querySelector('input[name="q"]');
    const resultsContainer = document.querySelector('.results');

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            if (searchInput.value.trim() === '') {
                // Clear search results when input is empty
                resultsContainer.innerHTML = '';
            }
        });
    }
});
