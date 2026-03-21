// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 03 - 레이아웃 패널 (Code-Behind)                 ■
// ■  계산기 로직                                           ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

using System;
using System.Windows;
using System.Windows.Controls;

namespace LessonWpf
{
    // ┌──────────────────────────────────────────────────┐
    // │  계산기 메인 윈도우                                │
    // └──────────────────────────────────────────────────┘
    // XAML에서 레이아웃(모양)을 정하고,
    // 여기서는 버튼을 눌렀을 때 어떤 일이 일어나는지를 정합니다.
    // XAML = 설계도, Code-Behind = 기계 내부 작동 원리
    public partial class MainWindow : Window
    {
        private string _currentInput = "0";  // 현재 입력 중인 숫자
        private string _formula = "";         // 전체 수식
        private double _result;               // 계산 결과
        private string _lastOperator = "";    // 마지막 연산자
        private bool _isNewInput = true;      // 새 숫자 입력 시작 여부

        public MainWindow()
        {
            InitializeComponent();
        }

        // ┌──────────────────────────────────────────┐
        // │  숫자 버튼 클릭                           │
        // └──────────────────────────────────────────┘
        // sender는 "누가 이 이벤트를 보냈는지" 알려줍니다.
        // 버튼의 Content(표시 글자)를 읽어서 숫자를 조합합니다.
        private void OnNumber(object sender, RoutedEventArgs e)
        {
            if (sender is Button button)
            {
                string digit = button.Content.ToString() ?? "";

                if (_isNewInput)
                {
                    _currentInput = digit == "." ? "0." : digit;
                    _isNewInput = false;
                }
                else
                {
                    // 소수점 중복 방지
                    if (digit == "." && _currentInput.Contains("."))
                        return;
                    _currentInput += digit;
                }

                ResultText.Text = _currentInput;
                StatusText.Text = $"입력: {_currentInput}";
            }
        }

        // ┌──────────────────────────────────────────┐
        // │  연산자 버튼 클릭 (+, -, ×, ÷)           │
        // └──────────────────────────────────────────┘
        private void OnOperator(object sender, RoutedEventArgs e)
        {
            if (sender is Button button)
            {
                string op = button.Content.ToString() ?? "";

                if (double.TryParse(_currentInput, out double value))
                {
                    Calculate(value);
                    _lastOperator = op;
                    _formula += $"{_currentInput} {op} ";
                    FormulaText.Text = _formula;
                    _isNewInput = true;
                }

                StatusText.Text = $"연산자: {op}";
            }
        }

        // ┌──────────────────────────────────────────┐
        // │  등호(=) 버튼 - 최종 계산                 │
        // └──────────────────────────────────────────┘
        private void OnEquals(object sender, RoutedEventArgs e)
        {
            if (double.TryParse(_currentInput, out double value))
            {
                Calculate(value);
                _formula += _currentInput;
                FormulaText.Text = _formula + " =";
                ResultText.Text = _result.ToString("G");
                _currentInput = _result.ToString("G");
                _formula = "";
                _lastOperator = "";
                _isNewInput = true;
                StatusText.Text = $"결과: {_result:G}";
            }
        }

        // ┌──────────────────────────────────────────┐
        // │  초기화 (CE) 버튼                         │
        // └──────────────────────────────────────────┘
        private void OnClear(object sender, RoutedEventArgs e)
        {
            _currentInput = "0";
            _formula = "";
            _result = 0;
            _lastOperator = "";
            _isNewInput = true;
            ResultText.Text = "0";
            FormulaText.Text = "0";
            StatusText.Text = "초기화됨";
        }

        // ┌──────────────────────────────────────────┐
        // │  실제 계산 수행                            │
        // └──────────────────────────────────────────┘
        private void Calculate(double value)
        {
            switch (_lastOperator)
            {
                case "+": _result += value; break;
                case "-": _result -= value; break;
                case "×": _result *= value; break;
                case "÷":
                    if (value != 0) _result /= value;
                    else
                    {
                        StatusText.Text = "오류: 0으로 나눌 수 없습니다!";
                        return;
                    }
                    break;
                default:
                    _result = value; // 첫 번째 숫자
                    break;
            }

            ResultText.Text = _result.ToString("G");
        }
    }
}
