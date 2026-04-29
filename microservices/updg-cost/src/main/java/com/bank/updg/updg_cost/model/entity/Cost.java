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
@TableName("pm_cost")
public class Cost {

    @TableId
    private String costId;

    private String projectId;

    private String costType;

    private BigDecimal amount;

    private LocalDateTime calculateTime;

    private BigDecimal evmPv;

    private BigDecimal evmEv;

    private BigDecimal evmAc;

    private LocalDateTime createTime;
}
