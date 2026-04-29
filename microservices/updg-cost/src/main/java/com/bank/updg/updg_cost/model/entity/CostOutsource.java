package com.bank.updg.updg_cost.model.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("pm_cost_outsource")
public class CostOutsource {

    @TableId
    private String outsourceCostId;

    private String costId;

    private String staffId;

    private String timesheetId;

    private BigDecimal amount;

    private LocalDateTime createTime;
}
