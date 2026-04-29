package com.bank.updg.updg_business.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.bank.updg.updg_business.model.entity.Customer;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface CustomerMapper extends BaseMapper<Customer> {
}
