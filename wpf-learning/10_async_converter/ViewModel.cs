// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 10 - ViewModel (비동기 작업 포함)                ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using System.Windows.Input;
using System.Windows.Media;

namespace LessonWpf
{
    // ┌──────────────────────────────────────────────────┐
    // │  ConverterViewModel                              │
    // └──────────────────────────────────────────────────┘
    public class ConverterViewModel : INotifyPropertyChanged
    {
        private string _celsiusValue = "100";
        private string _kmValue = "42.195";
        private string _kgValue = "70";
        private bool _isActive = true;
        private int _scoreValue = 85;
        private string _heightCm = "170";
        private string _weightKg = "65";
        private string _asyncInput = "";
        private string _validationResult = "입력값을 검증하려면 버튼을 누르세요.";
        private bool _isValidating;
        private Brush _validationColor = Brushes.Gray;

        public event PropertyChangedEventHandler? PropertyChanged;

        // ── 변환기에서 사용하는 속성들 ──
        public string CelsiusValue
        {
            get => _celsiusValue;
            set { _celsiusValue = value; OnPropertyChanged(); }
        }

        public string KmValue
        {
            get => _kmValue;
            set { _kmValue = value; OnPropertyChanged(); }
        }

        public string KgValue
        {
            get => _kgValue;
            set { _kgValue = value; OnPropertyChanged(); }
        }

        public bool IsActive
        {
            get => _isActive;
            set { _isActive = value; OnPropertyChanged(); }
        }

        public int ScoreValue
        {
            get => _scoreValue;
            set { _scoreValue = value; OnPropertyChanged(); }
        }

        public string HeightCm
        {
            get => _heightCm;
            set { _heightCm = value; OnPropertyChanged(); }
        }

        public string WeightKg
        {
            get => _weightKg;
            set { _weightKg = value; OnPropertyChanged(); }
        }

        // ┌──────────────────────────────────────────┐
        // │  비동기 검증 관련 속성                      │
        // └──────────────────────────────────────────┘
        public string AsyncInput
        {
            get => _asyncInput;
            set { _asyncInput = value; OnPropertyChanged(); }
        }

        public string ValidationResult
        {
            get => _validationResult;
            set { _validationResult = value; OnPropertyChanged(); }
        }

        public bool IsValidating
        {
            get => _isValidating;
            set { _isValidating = value; OnPropertyChanged(); }
        }

        public Brush ValidationColor
        {
            get => _validationColor;
            set { _validationColor = value; OnPropertyChanged(); }
        }

        public ICommand ValidateCommand { get; }

        public ConverterViewModel()
        {
            // ┌──────────────────────────────────────────┐
            // │  비동기 커맨드                             │
            // └──────────────────────────────────────────┘
            // 서버 검증을 시뮬레이션합니다.
            // 실제로는 네트워크 요청이 들어갈 자리!
            ValidateCommand = new AsyncRelayCommand(ValidateAsync,
                () => !string.IsNullOrWhiteSpace(AsyncInput) && !IsValidating);
        }

        // ┌──────────────────────────────────────────┐
        // │  비동기 검증 메서드                        │
        // └──────────────────────────────────────────┘
        // async/await는 "택배를 기다리면서 다른 일 하기"입니다.
        // Task.Delay로 서버 응답 대기를 시뮬레이션합니다.
        // 실제 앱에서는 HttpClient.GetAsync() 등을 사용합니다.
        private async Task ValidateAsync()
        {
            IsValidating = true;
            ValidationResult = "검증 중... (서버 응답 대기)";
            ValidationColor = Brushes.Gray;

            // 서버 응답 대기 시뮬레이션 (2초)
            // 이 동안 UI는 멈추지 않습니다! (ProgressBar가 돌아감)
            await Task.Delay(2000);

            // 검증 로직 (간단한 예시)
            if (AsyncInput.Length >= 3)
            {
                ValidationResult = $"'{AsyncInput}' 검증 성공! (유효한 입력입니다)";
                ValidationColor = Brushes.Green;
            }
            else
            {
                ValidationResult = $"'{AsyncInput}' 검증 실패! (3글자 이상 입력하세요)";
                ValidationColor = Brushes.Red;
            }

            IsValidating = false;
        }

        private void OnPropertyChanged([CallerMemberName] string? name = null)
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }

    // ┌──────────────────────────────────────────────────┐
    // │  AsyncRelayCommand - 비동기 작업용 커맨드         │
    // └──────────────────────────────────────────────────┘
    // 일반 RelayCommand와 비슷하지만,
    // Execute에서 async Task를 실행합니다.
    // 택배 기사(백그라운드)에게 배달을 맡기고
    // 나(UI)는 다른 일을 계속하는 방식!
    public class AsyncRelayCommand : ICommand
    {
        private readonly Func<Task> _execute;
        private readonly Func<bool>? _canExecute;
        private bool _isExecuting;

        public AsyncRelayCommand(Func<Task> execute, Func<bool>? canExecute = null)
        {
            _execute = execute;
            _canExecute = canExecute;
        }

        public bool CanExecute(object? parameter)
            => !_isExecuting && (_canExecute?.Invoke() ?? true);

        public async void Execute(object? parameter)
        {
            if (!CanExecute(parameter)) return;

            _isExecuting = true;
            try
            {
                await _execute();
            }
            finally
            {
                _isExecuting = false;
            }
        }

        public event EventHandler? CanExecuteChanged
        {
            add => CommandManager.RequerySuggested += value;
            remove => CommandManager.RequerySuggested -= value;
        }
    }

    // ── RelayCommand (동기 버전) ──
    public class RelayCommand : ICommand
    {
        private readonly Action _execute;
        private readonly Func<bool>? _canExecute;

        public RelayCommand(Action execute, Func<bool>? canExecute = null)
        {
            _execute = execute;
            _canExecute = canExecute;
        }

        public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;
        public void Execute(object? parameter) => _execute();

        public event EventHandler? CanExecuteChanged
        {
            add => CommandManager.RequerySuggested += value;
            remove => CommandManager.RequerySuggested -= value;
        }
    }
}
