const findMissingNumber = (nums) => {
  if (!nums || nums.length === 0) {
    return 0; // Or handle the empty array case as appropriate for your problem
  }

  const n = nums.length;
  const expectedSum = n * (n + 1) / 2; // Sum of numbers from 0 to n
  const actualSum = nums.reduce((sum, num) => sum + num, 0);

  return expectedSum - actualSum;
};

// Example Usage:
const numbers = [3, 0, 1];
const missing = findMissingNumber(numbers);
console.log(`Missing number: ${missing}`);

const numbers2 = [9,6,4,2,3,5,7,0,1];
const missing2 = findMissingNumber(numbers2);
console.log(`Missing number: ${missing2}`);

const numbers3 = [0,1];
const missing3 = findMissingNumber(numbers3);
console.log(`Missing number: ${missing3}`);