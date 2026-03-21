using System;

namespace ArchitectureLearning.Mvvm
{
    internal class Program
    {
        static void Main()
        {
            PrintHeader();
            Lesson1_ReadComputedProperties();
            Lesson2_WatchPropertyChangedEvents();
            Lesson3_ViewWouldOnlyReadViewModel();
        }

        static void PrintHeader()
        {
            Console.WriteLine(new string('=', 72));
            Console.WriteLine("MVVM 수업: ViewModel 속성이 바뀌면 화면이 따라오는 흐름");
            Console.WriteLine(new string('=', 72));
            Console.WriteLine();
        }

        static void Lesson1_ReadComputedProperties()
        {
            Console.WriteLine("[레슨 1] ViewModel이 화면용 속성을 계산해 주기");
            Console.WriteLine();

            var model = new StudentModel("지안", 74, 35);
            var viewModel = new StudentViewModel(model);

            Console.WriteLine(viewModel.Summary);
            Console.WriteLine("결과: " + viewModel.ResultText);
            Console.WriteLine("조언: " + viewModel.Advice);
            Console.WriteLine();
        }

        static void Lesson2_WatchPropertyChangedEvents()
        {
            Console.WriteLine("[레슨 2] 속성 변경 알림이 어떻게 화면 갱신 신호가 되는지 보기");
            Console.WriteLine();

            var model = new StudentModel("준호", 61, 20);
            var viewModel = new StudentViewModel(model);

            viewModel.PropertyChanged += (_, args) =>
            {
                Console.WriteLine($"  화면에게 알림: {args.PropertyName} 속성이 바뀌었습니다.");
            };

            viewModel.AddStudyMinutes(15);
            viewModel.ApplyRetestScore(78);
            Console.WriteLine("최종 요약: " + viewModel.Summary);
            Console.WriteLine("최종 조언: " + viewModel.Advice);
            Console.WriteLine();
        }

        static void Lesson3_ViewWouldOnlyReadViewModel()
        {
            Console.WriteLine("[레슨 3] View가 Model 대신 ViewModel만 보면 좋은 이유");
            Console.WriteLine();

            var model = new StudentModel("예나", 95, 50);
            var viewModel = new StudentViewModel(model);

            Console.WriteLine("View가 읽는 값: " + viewModel.Summary);
            Console.WriteLine("View가 읽는 값: " + viewModel.Advice);
            Console.WriteLine(
                "설명: 화면은 Score >= 70 같은 규칙을 몰라도 됩니다. " +
                "ViewModel이 이미 화면에 필요한 모양으로 바꿔 주기 때문입니다.");
            Console.WriteLine();
        }
    }
}
