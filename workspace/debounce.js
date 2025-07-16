const debounce = (func, delay) => {
  let timeoutId;

  return (...args) => {
    clearTimeout(timeoutId);

    timeoutId = setTimeout(() => {
      func(...args);
    }, delay);
  };
};

// Example Usage:
const logInput = (value) => {
  console.log(`Input Value: ${value}`);
};

const debouncedLogInput = debounce(logInput, 300); // Delay of 300ms

// Simulating input events
debouncedLogInput('a');
debouncedLogInput('ab');
debouncedLogInput('abc');
setTimeout(() => debouncedLogInput('abcd'), 400); // Only this one will log (after 400ms)
debouncedLogInput('abcdf'); // This one resets the timer before the 'abcd' call completes.
setTimeout(() => debouncedLogInput('abcdef'), 600);  // This one resets the timer before the 'abcd' call completes.
setTimeout(() => debouncedLogInput('abcdefg'), 800); //after all events called within the delay the function will be triggered