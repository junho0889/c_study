// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WPF 06 - 학생 목록 ViewModel                        ■
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
    // │  Student 모델 - 학생 데이터                       │
    // └──────────────────────────────────────────────────┘
    public class Student : INotifyPropertyChanged
    {
        private string _name = "";
        private string _grade = "1학년";
        private int _score;

        public event PropertyChangedEventHandler? PropertyChanged;

        public string Name
        {
            get => _name;
            set { _name = value; OnPropertyChanged(); }
        }

        public string Grade
        {
            get => _grade;
            set { _grade = value; OnPropertyChanged(); }
        }

        public int Score
        {
            get => _score;
            set
            {
                _score = Math.Clamp(value, 0, 100); // 0~100 범위 제한
                OnPropertyChanged();
                OnPropertyChanged(nameof(GradeLevel));
            }
        }

        // ── 점수에 따른 등급 (계산 속성) ──
        // 90점 이상 = A, 80점 이상 = B, ... 60점 미만 = F
        public string GradeLevel => _score switch
        {
            >= 90 => "A",
            >= 80 => "B",
            >= 70 => "C",
            >= 60 => "D",
            _ => "F"
        };

        private void OnPropertyChanged([CallerMemberName] string? name = null)
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }

    // ┌──────────────────────────────────────────────────┐
    // │  StudentViewModel - 학생 목록 관리                │
    // └──────────────────────────────────────────────────┘
    public class StudentViewModel : INotifyPropertyChanged
    {
        private string _inputName = "";
        private string _inputScore = "";
        private object? _inputGrade;
        private Student? _selectedStudent;
        private string _searchText = "";
        private string _statusText = "학생을 추가해 보세요!";
        private string _selectedStudentInfo = "학생을 선택하면 정보가 표시됩니다.";

        public event PropertyChangedEventHandler? PropertyChanged;

        // ── ObservableCollection ──
        // 항목이 추가/삭제되면 View에 자동으로 알려줍니다.
        // 학교 전광판처럼 - 학생이 전학오면 자동으로 이름이 표시!
        public ObservableCollection<Student> Students { get; } = new();

        // ── 필터링된 학생 목록 ──
        // 검색어에 맞는 학생만 보여줍니다
        public ObservableCollection<Student> FilteredStudents { get; } = new();

        public string InputName
        {
            get => _inputName;
            set { _inputName = value; OnPropertyChanged(); }
        }

        public string InputScore
        {
            get => _inputScore;
            set { _inputScore = value; OnPropertyChanged(); }
        }

        public object? InputGrade
        {
            get => _inputGrade;
            set { _inputGrade = value; OnPropertyChanged(); }
        }

        public Student? SelectedStudent
        {
            get => _selectedStudent;
            set
            {
                _selectedStudent = value;
                OnPropertyChanged();
                UpdateSelectedInfo();
            }
        }

        public string SearchText
        {
            get => _searchText;
            set
            {
                _searchText = value;
                OnPropertyChanged();
                ApplyFilter();
            }
        }

        public string StatusText
        {
            get => _statusText;
            set { _statusText = value; OnPropertyChanged(); }
        }

        public string SelectedStudentInfo
        {
            get => _selectedStudentInfo;
            set { _selectedStudentInfo = value; OnPropertyChanged(); }
        }

        public ICommand AddCommand { get; }
        public ICommand DeleteCommand { get; }

        public StudentViewModel()
        {
            AddCommand = new RelayCommand(AddStudent,
                () => !string.IsNullOrWhiteSpace(InputName));

            DeleteCommand = new RelayCommand(DeleteStudent,
                () => SelectedStudent != null);

            // 샘플 데이터
            Students.Add(new Student { Name = "김철수", Grade = "3학년", Score = 85 });
            Students.Add(new Student { Name = "이영희", Grade = "2학년", Score = 92 });
            Students.Add(new Student { Name = "박민수", Grade = "3학년", Score = 78 });
            Students.Add(new Student { Name = "정수진", Grade = "1학년", Score = 95 });
            Students.Add(new Student { Name = "최동현", Grade = "4학년", Score = 55 });

            ApplyFilter();
        }

        private void AddStudent()
        {
            int score = 0;
            int.TryParse(InputScore, out score);

            var student = new Student
            {
                Name = InputName,
                Grade = "1학년", // 기본값
                Score = score
            };
            Students.Add(student);
            ApplyFilter();
            StatusText = $"'{InputName}' 추가됨 - 총 {Students.Count}명";
            InputName = "";
            InputScore = "";
        }

        private void DeleteStudent()
        {
            if (SelectedStudent != null)
            {
                string name = SelectedStudent.Name;
                Students.Remove(SelectedStudent);
                ApplyFilter();
                StatusText = $"'{name}' 삭제됨 - 총 {Students.Count}명";
            }
        }

        // ── 검색 필터 적용 ──
        private void ApplyFilter()
        {
            FilteredStudents.Clear();
            var filtered = string.IsNullOrEmpty(SearchText)
                ? Students
                : new ObservableCollection<Student>(
                    Students.Where(s => s.Name.Contains(SearchText, StringComparison.OrdinalIgnoreCase)));

            foreach (var s in filtered)
                FilteredStudents.Add(s);

            StatusText = $"검색 결과: {FilteredStudents.Count}명 / 전체 {Students.Count}명";
        }

        private void UpdateSelectedInfo()
        {
            if (SelectedStudent != null)
            {
                var s = SelectedStudent;
                SelectedStudentInfo =
                    $"이름: {s.Name}\n" +
                    $"학년: {s.Grade}\n" +
                    $"점수: {s.Score}점\n" +
                    $"등급: {s.GradeLevel}";
            }
            else
            {
                SelectedStudentInfo = "학생을 선택하면 정보가 표시됩니다.";
            }
        }

        private void OnPropertyChanged([CallerMemberName] string? name = null)
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }

    // ── RelayCommand (05_commands_mvvm에서 가져온 것과 같은 구현) ──
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
