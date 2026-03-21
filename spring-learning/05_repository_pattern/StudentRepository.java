import java.util.HashMap;
import java.util.Map;

class StudentEntity {
    private final String name;
    private final int score;

    public StudentEntity(String name, int score) {
        this.name = name;
        this.score = score;
    }

    public String getName() {
        return name;
    }

    public int getScore() {
        return score;
    }
}

public class StudentRepository {
    private final Map<Long, StudentEntity> storage = new HashMap<>();

    public void save(Long id, StudentEntity student) {
        storage.put(id, student);
    }

    public StudentEntity findById(Long id) {
        return storage.get(id);
    }

    public static void main(String[] args) {
        StudentRepository repository = new StudentRepository();
        repository.save(1L, new StudentEntity("민수", 92));

        StudentEntity student = repository.findById(1L);
        System.out.println("[레슨 1] Repository 는 데이터를 꺼내고 넣는 창구");
        System.out.println("  저장된 학생: " + student.getName() + ", " + student.getScore() + "점");
    }
}
