module.exports = {
  '*.{ts,tsx}': ['eslint --fix', 'prettier --write'],
  '*.{js,jsx,mjs,cjs}': ['eslint --fix', 'prettier --write'],
  '*.{json,md,mdx}': ['prettier --write'],
  '*.{css,scss,sass}': ['prettier --write'],
};
