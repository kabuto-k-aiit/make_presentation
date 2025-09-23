interface PasswordValidationResult {
  isValid: boolean;
  errors: string[];
}

export const validatePassword = (password: string): PasswordValidationResult => {
  const errors: string[] = [];

  // 最小長チェック
  if (password.length < 8) {
    errors.push('パスワードは8文字以上である必要があります');
  }

  // 大文字を含むかチェック
  if (!/[A-Z]/.test(password)) {
    errors.push('パスワードは少なくとも1つの大文字を含む必要があります');
  }

  // 小文字を含むかチェック
  if (!/[a-z]/.test(password)) {
    errors.push('パスワードは少なくとも1つの小文字を含む必要があります');
  }

  // 数字を含むかチェック
  if (!/\d/.test(password)) {
    errors.push('パスワードは少なくとも1つの数字を含む必要があります');
  }

  // 特殊文字を含むかチェック
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('パスワードは少なくとも1つの特殊文字を含む必要があります');
  }

  // パスワードの強度スコアを計算（オプション）
  const strengthScore = [
    /[A-Z]/.test(password),  // 大文字
    /[a-z]/.test(password),  // 小文字
    /\d/.test(password),     // 数字
    /[!@#$%^&*(),.?":{}|<>]/.test(password),  // 特殊文字
    password.length >= 12,    // 12文字以上
  ].filter(Boolean).length;

  return {
    isValid: errors.length === 0,
    errors,
    strengthScore,
  };
};