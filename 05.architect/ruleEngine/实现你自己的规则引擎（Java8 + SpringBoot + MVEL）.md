# 引言

Rule-Engine 是一个专家系统程序，它对输入数据运行规则，如果任何条件匹配，它就会执行相应的操作，市场上有许多可用的规则引擎实现。但是，如果您想创建自己的简单规则引擎来满足您的大部分要求，那么我们开始吧。它可能无法满足所有要求，但您可以了解规则引擎的实现，并可以根据需要对其进行修改。

# 技术栈
我们将使用以下技术栈：
* SpringBoot 2.0.5.RELEASE：将规则引擎项目创建为 rest API。
* Maven：项目框架
* MVEL 2.4：编写规则的表达式语言。
* PostgreSQL 9.4 数据库：用于存储规则。
*  Spring JPA：用于数据库连接

# 架构图


我们按照上面的实现框架，一步步实现Rule-Engine。
* 我们使用 SpringBoot 和 Maven 框架将规则引擎实现为 Rest API。
* 了编写规则，我们使用表达式语言 (MVEL) 和一些特定领域的关键字
* 我们将规则存储在数据库 (pg) 中
* 我们实现了一个抽象推理引擎，用于实现不同领域特定的推理引擎。例如，我们可以在一个应用程序中同时编写贷款和保险相关的规则引擎。
* 我们实施关键字解析器来解析所有特定于域的关键字。
* 我们实现了两个解析器。一种用于解析 MVEL 表达式，另一种用于 DSL。
* 我们使用postman进行 API 测试的测试。

# 1.规则语言
* 规则是一组条件，后跟一组操作。规则主要以if-then形式表示。
* 为了编写规则，我们使用 MVEL expression language + Domain Specific Language 。
  > 则的语言 = MVEL + DSL
* DSL 或领域特定语言意味着，它不是 MVEL 的一部分。它是由我们自己为特定领域创建的。代替编写多个规则或表达式，我们可以将它们组合成一个，并可以使用关键字进行映射。 DSL 关键字使其易于使用和可重用。
  > 例如，要批准任何人的贷款，是否必须检查银行当年的目标是否完成？那么，为了在规则中提及它，我们可能需要在 MVEL 中编写多个语句或表达式。但是，如果我们创建一个关键字，如“bank.target_done”，它将返回一个简单的 true 或 false。在这个关键字后面，我们进行所有计算以获得当年的目标状态。现在我们可以在编写规则的任何地方使用它。
* 在此规则引擎中，我们对 DSL 使用以下格式，这与 MVEL 不同。
  > $(resolver-keyword.sub-keyword)
* Resolver 关键字可以看作是所有子关键字的键空间。例如，bank 是一个解析器关键字，所有与银行相关的关键字，如 interest_rate、targe_done 或 branch 等都是子关键字，经过一些计算后返回一些值。此格式用于将所有相同的相关关键字组合在一起。

## 例子
* 假设我们的需求是这样的，我们必须为贷款申请创建一个规则引擎，以下是批准贷款的规则。
  
```
Domain: Loan
Rule 1: A person is eligible for home loan?
if:
   1. He has monthly salary more than 50K.
   2. And his credit score is more than 800.
   3. And requested loan amount is less than 40L.
   4. And bank's current year target not done for home loan.
then:
   1. Approve the home loan.
   2. Sanction 80% of requested loan amount.
Rule 2: A person is eligible for home loan?
if:
   1. He has monthly salary more than 35K and less than 50K.
   2. And his credit score is less than 500.
   3. And requested loan amount is less than 20L.
   4. And bank's current year target not done for home loan.
then:
   1. Approve home loan.
   2. Sanction 60% of requested loan amount.
```
* 让我们将这些规则以 MVEL + DSL 的形式转换为存储在 DB 中。

## MVEL + DSL形式的规则：
```
#Loan Rule 1:
Condition:
     input.monthlySalary >= 50000 
     && input.creditScore >= 800 
     && input.requestedLoanAmount < 4000000 
     && $(bank.target_done) == false
Action:
     output.setApprovalStatus(true);
     output.setSanctionedPercentage(90); 
     output.setProcessingFees(8000);
#Loan Rule 2:
Condition:
     input.monthlySalary >= 35000 && input.monthlySalary <= 50000
     && input.creditScore <= 500 
     && input.requestedLoanAmount < 2000000 
     && $(bank.target_done) == false
Action:
     output.setApprovalStatus(true);
     output.setSanctionedPercentage(60); 
     output.setProcessingFees(2000);
```

* 在此示例中， $(bank.target_done) 是特定于域的关键字。这里将解决并返回有关贷款的银行状态，今年的住房贷款目标是否完成（真/假）? 除此以外，其他都是MVEL的表达形式。
* 另外，这里的 input 和 output 关键字代表两个 java 对象。输入对象作为输入数据传递给规则引擎，并根据该数据执行所有贷款规则。而最后，它会以输出对象的形式返回结果。
* 在这个例子中，我们有 UserDetails 是一个输入对象，LoanDetails 是一个输出结果对象。

tu2

* Input Data:

```
public class UserDetails {
    Double monthlySalary;
    Integer creditScore;
    Double requestedLoanAmount;
    //Few other variables
}
```

* Output Result:
  
```
public class LoanDetails {
    Boolean approvalStatus;
    Float sanctionedPercentage;
    Double processingFees;
    //Few other variables
}
```

# 2. 在数据库中存储规则
* 以后将这些规则写成MVEL+DSL的形式，存储在Postgres DB中。您可以根据您的可行性使用任何其他数据库。

如果您已经拥有 Postgres，则创建数据库 rulebase 并在其中创建一个名为 rules 的表。在这个表中，我们提到了几个类似column的priority，rule id等具体使用（见第4节：“创建Rule的模型类”）。

```
CREATE DATABASE rulebase;
CREATE TABLE rules (
 rule_namespace varchar(256) not null, 
 rule_id varchar(512) not null, 
 condition varchar(2000), 
 action varchar(2000), 
 priority integer, 
 description varchar(1000), 
 PRIMARY KEY(rule_namespace, rule_id)
);
```
* 现在借助以下查询将上述两条规则插入到 Postgres 数据库中。

```
LOAN RULE 1
INSERT INTO rules 
 (rule_namespace , rule_id, condition, 
 action, priority, description) 
VALUES (
 'LOAN',
 '1',
 'input.monthlySalary >= 50000 && input.creditScore >= 800 && input.requestedLoanAmount < 4000000 && $(bank.target_done) == false', 
 'output.setApprovalStatus(true);output.setSanctionedPercentage(90);output.setProcessingFees(8000);', 
 '1', 
 'A person is eligible for Home loan?'
);
LOAN RULE 2
INSERT INTO rules 
 (rule_namespace , rule_id, condition, 
 action, priority, description) 
VALUES (
 'LOAN',
 '2',
 'input.monthlySalary >= 35000 && input.monthlySalary <= 50000 && input.creditScore <= 500 && input.requestedLoanAmount < 2000000 && $(bank.target_done) == false',
'output.setApprovalStatus(true);output.setSanctionedPercentage(60);output.setProcessingFees(2000);', 
 '2', 
 'A person is eligible for Home loan?'
);
```

# 3.创建一个Maven项目
* 首先创建一个maven工程，在pom文件中添加如下spring-boot、Postgres、MVEL等依赖。
  
```
parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.0.5.RELEASE</version>
</parent>
<properties>
    <java.version>1.8</java.version>
    <junit.version>4.12</junit.version>
    <postgresql.version>9.4-1206-jdbc42</postgresql.version>
    <mvel.version>2.4.4.Final</mvel.version>
</properties>
<dependencies>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
        </dependency>
<dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
<dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
<dependency>
            <groupId>org.mve</groupId>
            <artifactId>mvel2</artifactId>
        </dependency>
<dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
        </dependency>
</dependencies>
```
# 4.为Rule创建模型类
* 基本上，规则采用 if-then 形式。它基本上包含两部分，条件和动作。但是我们必须定义更多的信息来实现它。那些是：
  * 命名空间：用于识别或将域的相同类型的规则合并为一个。
  * Id：每个规则都可以用一些唯一的 Id 来标识。
  * Action：MVEL+DSL形式的Rule动作。
  * 优先级：它将用于决定应首先对输入数据执行哪个规则。
  * 描述：显示规则的描述。
* 为了存储所有这些信息，我们使用规则模型。
```
  public class Rule {
    RuleNamespace ruleNamespace;
    String ruleId;
    String condition;
    String action;
    Integer priority;
    String description;
}
```

* 以枚举的形式描述规则的域（Rule namespace）
```
public enum RuleNamespace {
    LOAN,
    INSURANCE
}
```

# 5.数据库连接服务
对于数据库连接，我们使用 Spring Data JPA。现在首先在资源目录中添加 application.properties 并写入 PostgreSql URL 和凭据。

```
spring.datasource.url=jdbc:postgresql://localhost:5432/rulebase
spring.datasource.username=<your postgre username>
spring.datasource.password=<your postgre password>
spring.jpa.generate-ddl=true
```

现在创建数据库模型和存储库以从 Postgres DB 访问数据。为了实现它，我们使用 Spring Data JPA。为此，我们创建了一个存储库 RulesRepository 、数据库模型 RuleDbModel 和服务 KnowledgeBaseService 。
DB Model：从 DB 获取数据到 RuleDbModel 形式。

```
@Table(name = "rules")
public class RuleDbModel {
@Id
@Column(name = "rule_namespace")
    private String ruleNamespace;
@Column(name = "rule_id")
    private String ruleId;
@Column(name = "condition")
    private String condition;
@Column(name = "action")
    private String action;
@Column(name = "priority")
    private Integer priority;
@Column(name = "description")
    private String description;
@Data
    static class IdClass implements Serializable {
        private String ruleNamespace;
        private String ruleId;
    }
}
```
Repository：在 RulesRepository 类中定义数据库查询或函数。

```
@Repository
public interface RulesRepository extends JpaRepository<RuleDbModel, Long> {
    List<RuleDbModel> findByRuleNamespace(String ruleNamespace);
    List<RuleDbModel> findAll();
}
```

知识库服务：根据我们的要求定义访问规则的方法。

```
@Service
public class KnowledgeBaseService {
    @Autowired
    private RulesRepository rulesRepository;
public List<Rule> getAllRules(){
       //See complete code on git.
    }
public List<Rule> getAllRuleByNamespace(String ruleNamespace){
       //See complete code on git.
    }
}
```

6.DSL解析器：

要解析 DSL 相关关键字，我们需要实现一个关键字解析器。

DSL解析器接口：
```
public interface DSLResolver {
    String getResolverKeyword();
    Object resolveValue(String keyword);
}

```

该接口将由每个域特定的关键字来实现。例如，BankResolver 用于获取当前利率和目标完成与否的信息。
假设这里的解析器关键字是 bank ，子关键字是 interest 和 target_done 。然后是 BankResolver 的代码：
```
public class BankResolver implements DSLResolver {
    private static final String RESOLVER_KEYWORD = "bank";
    private static final String INTEREST = "interest";
    private static final String TARGET_DONE = "target_done";
@Override
    public String getResolverKeyword() {
        return RESOLVER_KEYWORD;
    }
@Override
    public Object resolveValue(String keyword) {
        if (keyword.equalsIgnoreCase(INTEREST)){
            //Code to calculate the current variable interest rates.
            return 9.0;
        }
if (keyword.equalsIgnoreCase(TARGET_DONE)){
            //Code to see the bank target of giving loan for this current year is done or not.
            return false;
        }
return null;
    }
}
```

# DSL 关键字解析器：
我们编写一个服务 DSLKeywordResolver 来解析所有已实现的关键字。这里 getResolver(String keyword) 方法解析解析器关键字并返回该关键字解析器的对象引用（示例：BankResolver）。

```
public class DSLKeywordResolver {
    Map<String, DSLResolver> dslKeywordResolverList;
@Autowired
    public DSLKeywordResolver(List<DSLResolver> resolverList) {
        dslKeywordResolverList = resolverList.stream()
                .collect(Collectors.toMap(DSLResolver::getResolverKeyword, Function.identity()));
    }
public Optional<DSLResolver> getResolver(String keyword) {
        return Optional.ofNullable(dslKeywordResolverList.get(keyword));
    }
}
```

现在编写 DSLParser，它采用给定的规则表达式并解析 DSL 关键字，并将规则表达式中的值替换为相应的关键字。

Example:

```
condition: “input.monthlySalary >= 50000 && input.creditScore >= 800 && input.requestedLoanAmount<4000000 && $(bank.target_done) == false”
条件：“input.monthlySalary >= 50000 && input.creditScore >= 800 && input.requestedLoanAmount<4000000 && $(bank.target_done) == false”

```

TO

```
condition: “input.monthlySalary >= 50000 && input.cibilScore >= 800 && input.requestedLoanAmount<4000000 && false == false”
条件：“input.monthlySalary >= 50000 && input.cibilScore >= 800 && input.requestedLoanAmount<4000000 && false == false”
```

```
public class DSLParser {
@Autowired
    private DSLKeywordResolver keywordResolver;
public String resolveDomainSpecificKeywords(String expression){
        Map<String, Object> dslKeywordToResolverValueMap = executeDSLResolver(expression);
        return replaceKeywordsWithValue(expression, dslKeywordToResolverValueMap);
    }
}
```

# 7. MVEL 解析器
解析 DSL 关键字后，表达式将充满 MVEL 表达式。现在我们创建一个 MVELParser 来解析这个 MVEL 表达式。

```
public class MVELParser {
public boolean parseMvelExpression( String expression, Map<String, Object> inputObjects){
        try {
            return MVEL.evalToBoolean(expression,inputObjects);
        }catch (Exception e){
            log.error("Can not parse Mvel Expression : {} Error: {}", expression, e.getMessage());
        }
        return false;
    }
}
```

这里的 inputObjects 包含输入数据和输出结果对象相对于输入和输出键的映射。

## 8. RuleParser

RuleParser 是 MVELParser 和 DSLParser 的包装器。它用于解析规则的条件和操作。条件对输入数据执行，动作执行返回输出结果。
规则解析器分两步解析规则表达式：
步骤 1) 首先解析特定领域的关键字：$(resolver-keyword.sub-keyword)
步骤 2) 解析 MVEL 表达式。

```
public class RuleParser<INPUT_DATA, OUTPUT_RESULT> {
@Autowired
    protected DSLParser dslParser;
    @Autowired
    protected MVELParser mvelParser;
private final String INPUT_KEYWORD = "input";
    private final String OUTPUT_KEYWORD = "output";
public boolean parseCondition(String expression, INPUT_DATA inputData) {
        String resolvedDslExpression = dslParser.resolveDomainSpecificKeywords(expression);
        Map<String, Object> input = new HashMap<>();
        input.put(INPUT_KEYWORD, inputData);
        boolean match = mvelParser.parseMvelExpression(resolvedDslExpression, input);
        return match;
    }
public OUTPUT_RESULT parseAction(String expression, INPUT_DATA inputData, OUTPUT_RESULT outputResult) {
        String resolvedDslExpression = dslParser.resolveDomainSpecificKeywords(expression);
        Map<String, Object> input = new HashMap<>();
        input.put(INPUT_KEYWORD, inputData);
        input.put(OUTPUT_KEYWORD, outputResult);
        mvelParser.parseMvelExpression(resolvedDslExpression, input);
        return outputResult;
    }
}
```

# 9.推理机
* 推理机是规则引擎的核心部分。它主要分三步对输入数据执行规则
  * 匹配：将事实/条件和数据与规则集进行匹配。它返回一组满足的规则。
  * RESOLVE：解决冲突的规则集，给出选中的一条规则。
  * EXECUTE：对给定数据运行所选规则的操作并返回结果输出。

我们在推理引擎的抽象类中实现所有三个步骤或方法，并在运行方法中调用它们。

```
public abstract class InferenceEngine<INPUT_DATA, OUTPUT_RESULT> {
@Autowired
    private RuleParser<INPUT_DATA, OUTPUT_RESULT> ruleParser;
public OUTPUT_RESULT run (List<Rule> listOfRules, INPUT_DATA inputData){
//STEP 1 MATCH
        List<Rule> conflictSet = match(listOfRules, inputData);
//STEP 2 RESOLVE
        Rule resolvedRule = resolve(conflictSet);
        if (null == resolvedRule){
            return null;
        }
//STEP 3 EXECUTE
        OUTPUT_RESULT outputResult = executeRule(resolvedRule, inputData);
return outputResult;
    }
//Here we are using Linear matching algorithm for pattern
    protected List<Rule> match(List<Rule> listOfRules, INPUT_DATA inputData){
        return listOfRules.stream()
                .filter(
                        rule -> {
                            String condition = rule.getCondition();
                            return ruleParser.parseCondition(condition, inputData);
                        }
                )
                .collect(Collectors.toList());
    }
//Here we are using find first rule logic.
    protected Rule resolve(List<Rule> conflictSet){
        Optional<Rule> rule = conflictSet.stream()
                .findFirst();
        if (rule.isPresent()){
            return rule.get();
        }
        return null;
    }
protected OUTPUT_RESULT executeRule(Rule rule, INPUT_DATA inputData){
        OUTPUT_RESULT outputResult = initializeOutputResult();
        return ruleParser.parseAction(rule.getAction(), inputData, outputResult);
    }
protected abstract OUTPUT_RESULT initializeOutputResult();
    protected abstract RuleNamespace getRuleNamespace();
}
```

这里另外两个抽象方法 initializeOutputResult() 和 getRuleNamespace() 在扩展的特定领域推理引擎中实现。 initializeOutputResult() 方法返回输出结果对象的初始化引用。 getRuleNamespace() 方法返回该推理引擎的 RuleNamespace

示例：为了为贷款应用程序或域创建规则引擎，我们必须扩展 InferenceEngine 并且需要实现两个抽象方法。对于此推理引擎，INPUT_DATA 将是 UserDetails 对象，而 OUTPUT_RESULT 将是 LoanDetails 对象。

```
public class LoanInferenceEngine extends InferenceEngine<UserDetails, LoanDetails> {
@Override
    protected RuleNamespace getRuleNamespace() {
        return RuleNamespace.LOAN;
    }
@Override
    protected LoanDetails initializeOutputResult() {
        return new LoanDetails();
    }
}
```

* 同样，我们也可以为其他领域创建推理引擎。例如保险。
```
public class InsuranceInferenceEngine extends InferenceEngine<PolicyHolderDetails, InsuranceDetails> {
@Override
    protected RuleNamespace getRuleNamespace() {
        return RuleNamespace.INSURANCE;
    }
@Override
    protected LoanDetails initializeOutputResult() {
        return new InsuranceDetails();
    }
}
``` 
对于保险推理引擎，INPUT_DATA 将是 PolicyHolderDetails 对象，而 OUTPUT_RESULT 将是 InsuranceDetails 对象。

# 10. 规则引擎 REST API
到目前为止，大部分规则引擎的实现已经完成。现在我们必须创建一个 rest API 或控制器以将输入作为 JSON 传递并从规则引擎获取响应。这里我们创建了两个rest controller，一个 /get-all-rules 用于获取所有规则，另一个 /loan 用于传递JSON格式的输入数据对象并获取规则执行的结果。
```
@RestController
public class RuleEngineRestController {
@GetMapping(value = "/get-all-rules")
    public ResponseEntity<?> getAllRules() {
        List<Rule> allRules = knowledgeBaseService.getAllRules();
        return ResponseEntity.ok(allRules);
    }
@PostMapping(value = "/loan")
    public ResponseEntity<?> runLoanRuleEngine(@RequestBody UserDetails userDetails) {
        LoanDetails result = (LoanDetails) ruleEngine.run(loanInferenceEngine, userDetails);
        return ResponseEntity.ok(result);
    }
}
```

# 11. Testing
现在我们的规则引擎准备好了。是时候测试它了。为了测试规则引擎 API，我们将使用 postman 工具
首先，让我们查看控制器 /get-all-rules 并从数据库中获取所有规则。

图3

其次，让我们通过 postman 以 JSON 格式发布输入对象 UserDetails 并查看响应。
输入 JSON：根据给定的输入数据规则 1 应该满足并且 Sanctioned Percentage 应该是 90 作为响应。

Input JSON:

```
{
 "creditScore": 900,
 "firstName": "Mark",
 "lastName": "K",
 "age": "25",
 "accountNumber": 123456789,
 "bank": "ABC BANK",
 "requestedLoanAmount": 3500000.0,
 "monthlySalary": 70000.0
}
```

Output Result:

上述测试我们也编写了SpringBoot JUnit测试。你可以在 git 上查看这里。

git地址 https://github.com/Rameshkatiyar/rules-engine
