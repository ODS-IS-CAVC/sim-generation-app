package com.catalogap.infrastructure.repository.mybatis.generated.mapper;

import com.catalogap.infrastructure.repository.mybatis.generated.entity.NearmissInfo;
import com.catalogap.infrastructure.repository.mybatis.generated.entity.NearmissInfoExample;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface NearmissInfoMapper {
    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    long countByExample(NearmissInfoExample example);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    int deleteByExample(NearmissInfoExample example);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    int deleteByPrimaryKey(Integer id);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    int insert(NearmissInfo record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    int insertSelective(NearmissInfo record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    List<NearmissInfo> selectByExample(NearmissInfoExample example);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    NearmissInfo selectByPrimaryKey(Integer id);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    int updateByExampleSelective(@Param("record") NearmissInfo record, @Param("example") NearmissInfoExample example);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    int updateByExample(@Param("record") NearmissInfo record, @Param("example") NearmissInfoExample example);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    int updateByPrimaryKeySelective(NearmissInfo record);

    /**
     * This method was generated by MyBatis Generator.
     * This method corresponds to the database table nearmiss_info
     *
     * @mbg.generated
     */
    int updateByPrimaryKey(NearmissInfo record);
}