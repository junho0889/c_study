// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 05 - MVVM ViewModel + RelayCommand              ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Windows.Input;

namespace LessonWpf
{
    // ┌──────────────────────────────────────────────────┐
    // │  1부: TodoItem - Model (데이터)                   │
    // └──────────────────────────────────────────────────┘
    // Model은 순수한 데이터입니다.
    // 도서관의 책 카드에 적힌 정보(제목, 저자)처럼
    // 할 일의 제목과 완료 여부를 저장합니다.
    public class TodoItem : INotifyPropertyChanged
    {
        private string _title = "";
        private bool _isCompleted;

        public event PropertyChangedEventHandler? PropertyChanged;

        public string Title
        {
            get => _title;
            set { _title = value; OnPropertyChanged(); }
        }

        public bool IsCompleted
        {
            get => _isCompleted;
            set { _isCompleted = value; OnPropertyChanged(); }
        }

        private void OnPropertyChanged([CallerMemberName] string? name = null)
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }

    // ┌──────────────────────────────────────────────────┐
    // │  2부: RelayCommand - ICommand 구현                │
    // └──────────────────────────────────────────────────┘
    // ICommand는 "명령서"입니다.
    // 버튼에 Click 이벤트 대신 Command를 연결하면:
    //   - Execute:    명령 실행 (주문 처리)
    //   - CanExecute: 실행 가능 여부 (품절이면 주문 불가)
    //
    // RelayCommand는 ICommand를 쉽게 만들어주는 도우미입니다.
    // 매번 새 클래스를 만들지 않고, 람다(짧은 함수)로 간단히 만듭니다.
    public class RelayCommand : ICommand
    {
        private readonly Action _execute;
        private readonly Func<bool>? _canExecute;

        public RelayCommand(Action execute, Func<bool>? canExecute = null)
        {
            _execute = execute;
            _canExecute = canExecute;
        }

        // CanExecute: "이 명령을 실행할 수 있나?" 확인
        // false를 반환하면 버튼이 자동으로 비활성화됩니다!
        public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;

        // Execute: 명령 실행
        public void Execute(object? parameter) => _execute();

        // CanExecuteChanged: 실행 가능 여부가 바뀌었음을 알림
        public event EventHandler? CanExecuteChanged
        {
            add => CommandManager.RequerySuggested += value;
            remove => CommandManager.RequerySuggested -= value;
        }
    }

    // ┌──────────────────────────────────────────────────┐
    // │  3부: TodoViewModel - 웨이터 (중간 관리자)        │
    // └──────────────────────────────────────────────────┘
    // ViewModel은 레스토랑의 웨이터입니다.
    //   - View(손님)에서 오는 명령(주문)을 받고
    //   - Model(주방)에서 데이터(요리)를 가져오고
    //   - 결과를 View에 전달합니다.
    //
    // View는 ViewModel만 알면 됩니다. Model을 직접 건드리지 않아요!
    public class TodoViewModel : INotifyPropertyChanged
    {
        private string _newTodoText = "";
        private string _statusText = "할 일을 입력하세요!";
        private TodoItem? _selectedItem;

        public event PropertyChangedEventHandler? PropertyChanged;

        // ── 속성: View와 바인딩되는 데이터 ──

        // ObservableCollection: 항목이 추가/삭제되면 자동으로 View에 알림!
        // 일반 List는 변경을 알리지 않지만,
        // ObservableCollection은 "새 학생이 왔어요!" 자동 방송을 합니다.
        public ObservableCollection<TodoItem> TodoItems { get; } = new();

        public string NewTodoText
        {
            get => _newTodoText;
            set { _newTodoText = value; OnPropertyChanged(); }
        }

        public string StatusText
        {
            get => _statusText;
            set { _statusText = value; OnPropertyChanged(); }
        }

        public TodoItem? SelectedItem
        {
            get => _selectedItem;
            set { _selectedItem = value; OnPropertyChanged(); }
        }

        // ── 커맨드: View의 버튼과 연결되는 명령 ──

        public ICommand AddCommand { get; }
        public ICommand ClearCompletedCommand { get; }
        public ICommand ClearAllCommand { get; }

        public TodoViewModel()
        {
            // AddCommand: 새 할 일 추가
            // 두 번째 인자(canExecute): 텍스트가 비어있으면 버튼 비활성화
            AddCommand = new RelayCommand(
                execute: () =>
                {
                    TodoItems.Add(new TodoItem { Title = NewTodoText });
                    StatusText = $"'{NewTodoText}' 추가됨 - 총 {TodoItems.Count}개";
                    NewTodoText = "";
                },
                canExecute: () => !string.IsNullOrWhiteSpace(NewTodoText)
            );

            // ClearCompletedCommand: 완료된 항목만 삭제
            ClearCompletedCommand = new RelayCommand(
                execute: () =>
                {
                    var completed = TodoItems.Where(t => t.IsCompleted).ToList();
                    foreach (var item in completed)
                        TodoItems.Remove(item);
                    StatusText = $"{completed.Count}개 완료 항목 삭제됨";
                },
                canExecute: () => TodoItems.Any(t => t.IsCompleted)
            );

            // ClearAllCommand: 전체 삭제
            ClearAllCommand = new RelayCommand(
                execute: () =>
                {
                    TodoItems.Clear();
                    StatusText = "모든 항목이 삭제되었습니다.";
                },
                canExecute: () => TodoItems.Count > 0
            );

            // 샘플 데이터
            TodoItems.Add(new TodoItem { Title = "WPF MVVM 패턴 공부하기" });
            TodoItems.Add(new TodoItem { Title = "ICommand 인터페이스 이해하기" });
            TodoItems.Add(new TodoItem { Title = "RelayCommand 직접 구현해보기", IsCompleted = true });
        }

        private void OnPropertyChanged([CallerMemberName] string? name = null)
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }
}
